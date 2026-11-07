from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from arquivos import interpretar_csv, ler_csv, ler_json
from processamento import numero, processar, normalizar, normalizar_vinculos, Tarifa, Vinculo
from analise import fotografia, resumir, media
from baixar_dados import gerar_vinculos
from visualizacao import criar_mapa

BASE=Path(__file__).resolve().parents[1]/'dados'

@pytest.fixture
def linha():
    return dict(ler_csv(BASE/'exemplo_sintetico.csv')[0])

@pytest.mark.parametrize('entrada,esperado',[('1.234,56','1234.56'),(',00','0'),('0,00','0'),('1234.56','1234.56')])
def test_numeros(entrada,esperado):
    assert numero(entrada)==Decimal(esperado)

@pytest.mark.parametrize('valor',['','NaN','Infinity','-10','1,2,3','abc','1.23,45'])
def test_numero_invalido(valor):
    with pytest.raises(ValueError): numero(valor)

def test_conversao_imutabilidade(linha):
    original=dict(linha)
    tarifa=normalizar(linha)
    assert tarifa.total==Decimal('0.5')
    assert linha==original
    with pytest.raises(FrozenInstanceError): tarifa.te=Decimal(1)

def test_kwh_sem_divisao_novamente(linha):
    tarifa=normalizar({**linha,'DscUnidadeTerciaria':'kWh','VlrTE':'0,2','VlrTUSD':'0,3'})
    assert tarifa.total==Decimal('0.5')

@pytest.mark.parametrize('campo,valor',[('DscSubClasse','Baixa Renda'),('DscModalidadeTarifaria','Branca'),
    ('DscBaseTarifaria','Base Econômica'),('DscDetalhe','SCEE'),('NomPostoTarifario','Ponta'),
    ('SigAgenteAcessante','EMPRESA ESPECÍFICA'),('DscClasse','Industrial')])
def test_perfis_nao_misturados(linha,campo,valor):
    r=processar((linha,{**linha,campo:valor}))
    assert len(r.tarifas)==1 and r.fora_recorte==1

@pytest.mark.parametrize('campo,valor',[('DscUnidadeTerciaria','kW'),('VlrTE',''),
    ('DatInicioVigencia','31/02/2024'),('DatFimVigencia','2023-01-01'),('NumCNPJDistribuidora','1.234E10')])
def test_invalido_diagnosticado(linha,campo,valor):
    r=processar(({**linha,campo:valor},))
    assert len(r.problemas)==1 and not r.tarifas

def test_coluna_ausente(linha):
    incompleta={k:v for k,v in linha.items() if k!='VlrTE'}
    with pytest.raises(ValueError,match='VlrTE'): processar((incompleta,))

def vinculo(t,uf='AC'):
    return Vinculo(t.cnpj,uf,date(2024,1,1),date(2025,12,31),'teste sintético')

def test_periodos_e_limites(linha):
    a=normalizar(linha)
    b=replace(a,inicio=date(2025,1,1),fim=date(2025,12,31),te=Decimal('0.4'))
    assert fotografia((a,b),(vinculo(a),),date(2024,12,31)).itens[0].tarifa.total==Decimal('0.5')
    assert fotografia((a,b),(vinculo(a),),date(2025,1,1)).itens[0].tarifa.total==Decimal('0.7')

def test_duplicatas_nao_enviesam_media(linha):
    a=normalizar(linha)
    b=replace(a,cnpj='00000000000999',te=Decimal('0.6'))
    foto=fotografia((a,a,a,b),(vinculo(a),vinculo(a),vinculo(b)),date(2024,12,31))
    resumo=resumir(foto.itens)[0]
    assert resumo.quantidade==2 and resumo.media==Decimal('0.7')

def test_conflito_excluido_sem_escolha_arbitraria(linha):
    a=normalizar(linha)
    b=replace(a,te=Decimal('0.21'))
    foto=fotografia((a,b),(vinculo(a),),date(2024,12,31))
    assert foto.conflitos==(a.cnpj,) and foto.itens==()

def test_conflito_componentes_mesmo_total(linha):
    a=normalizar(linha)
    b=replace(a,te=Decimal('0.3'),tusd=Decimal('0.2'))
    assert fotografia((a,b),(vinculo(a),),date(2024,1,1)).conflitos

def test_distribuidora_multiplas_ufs_e_sem_mapa(linha):
    a=normalizar(linha)
    b=replace(a,cnpj='00000000000999')
    foto=fotografia((a,b),(vinculo(a),vinculo(a,'AM')),date(2024,1,1))
    assert {i.uf for i in foto.itens}=={'AC','AM'}
    assert foto.sem_mapeamento==(b.cnpj,)

def test_sem_dados_nao_e_zero():
    assert media(()) is None
    assert len(resumir(()))==27
    assert all(r.media is None for r in resumir(()))

def test_csv_bom_acentos_espacos(linha):
    bruto='\ufeff Nome ;Valor\r\nAção;"1,23"\r\n'.encode('utf-8')
    assert interpretar_csv(bruto)==({'Nome':'Ação','Valor':'1,23'},)

def test_csv_malformado():
    with pytest.raises(ValueError): interpretar_csv(b'A;B\n1;2;3')

def test_mapeamento_nao_extrapola_mes():
    rows=({'NumCNPJ':'1','CodMunicipioIBGE':'1200401','DatReferenciaInformada':'2024-12-01','QtdUCAtiva':'10'},)
    vs=normalizar_vinculos(gerar_vinculos(rows))
    assert vs[0].uf=='AC' and vs[0].fim==date(2024,12,31)
    assert gerar_vinculos(({**rows[0],'QtdUCAtiva':'0'},))==()

def test_mapa_27_ufs_mesmo_sem_tarifas():
    geo=ler_json(BASE/'brasil_ufs.geojson')
    fig=criar_mapa(resumir(()),geo)
    assert len(geo['features'])==27 and len(fig.data[0].locations)==27
    assert fig.layout.map.style=='white-bg'

def test_integracao_dados_reais():
    r=processar(ler_csv(BASE/'tarifas_aneel.csv'))
    vs=normalizar_vinculos(ler_csv(BASE/'mapeamento_aneel.csv'))
    assert not r.problemas
    for ano in (2024,2025):
        f=fotografia(r.tarifas,vs,date(ano,12,31))
        assert len({i.uf for i in f.itens})==27
        assert len({(i.uf,i.tarifa.cnpj) for i in f.itens})==len(f.itens)
