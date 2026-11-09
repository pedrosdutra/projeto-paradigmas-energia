"""Coleta reproduzível. Rede e gravação ficam separadas do núcleo funcional."""
import argparse
import calendar
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from arquivos import salvar_csv
from processamento import CODIGOS_UF, normalizar_cnpj, numero

BASE = 'https://dadosabertos.aneel.gov.br/api/3/action/'
TARIFAS_ID = 'fcf2906c-7c32-4b9b-a637-054e7a5234f4'
INDGER_ID = 'fd10c9d4-cb76-4020-a322-e79afb13eaf7'
CSV_OFICIAL = 'https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv'
GEO_URL = 'https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=UF'
FILTRO_API = {'DscSubGrupo':'B1','DscModalidadeTarifaria':'Convencional',
              'DscClasse':'Residencial','DscSubClasse':'Residencial',
              'DscBaseTarifaria':'Tarifa de Aplicação'}
PASTA = Path(__file__).resolve().parent / 'dados'

def obter(url):
    with urlopen(Request(url,headers={'User-Agent':'ProjetoAcademicoTarifas/1.0'}),timeout=90) as resposta:
        raw=resposta.read()
    return gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw

def consultar(recurso, filtros, campos=None):
    """Paginação completa; falha se o total variar durante a coleta."""
    registros=[]
    total=None
    while total is None or len(registros)<total:
        parametros={'resource_id':recurso,'filters':json.dumps(filtros),
                    'limit':5000,'offset':len(registros),'sort':'_id asc'}
        if campos:
            parametros['fields']=','.join(campos)
        pagina=json.loads(obter(BASE+'datastore_search?'+urlencode(parametros)))
        if not pagina.get('success'):
            raise RuntimeError(f'Consulta recusada: {pagina.get("error")}')
        resultado=pagina['result']
        if total is not None and resultado['total'] != total:
            raise RuntimeError('A base mudou durante a coleta. Execute novamente.')
        total=resultado['total']
        novos=resultado['records']
        if not novos and len(registros)<total:
            raise RuntimeError('Paginação incompleta: a coleta foi interrompida')
        registros.extend(novos)
    return tuple(registros)

def gerar_vinculos(registros):
    """Evidência de atendimento municipal, válida somente no mês observado.

    Não usa endereço da sede, não presume exclusividade e não extrapola anos.
    UC ativa > 0 comprova presença observada; ausência não comprova não atuação.
    """
    codigos=dict(CODIGOS_UF)
    resultado=set()
    for r in registros:
        if numero(r['QtdUCAtiva']) <= 0:
            continue
        municipio=str(r['CodMunicipioIBGE']).strip()
        if len(municipio)!=7 or not municipio.isdigit() or municipio[:2] not in codigos:
            raise ValueError(f'Código de município inválido: {municipio}')
        inicio=date.fromisoformat(r['DatReferenciaInformada'])
        fim=date(inicio.year,inicio.month,calendar.monthrange(inicio.year,inicio.month)[1])
        fonte=f'https://dadosabertos.aneel.gov.br/dataset/indger-indicadores-gerenciais-da-distribuicao/resource/{INDGER_ID}'
        resultado.add((normalizar_cnpj(r['NumCNPJ']),codigos[municipio[:2]],
                       inicio.replace(day=1).isoformat(),fim.isoformat(),fonte))
    return tuple(dict(zip(('CNPJ','UF','Inicio','Fim','Fonte'),v)) for v in sorted(resultado))

def hash_arquivo(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anos',type=int,nargs='+',default=[2024,2025],help='Dezembro de cada ano para evidência geográfica')
    args=parser.parse_args()
    PASTA.mkdir(exist_ok=True)
    tarifas=consultar(TARIFAS_ID,FILTRO_API)
    if not tarifas:
        raise RuntimeError('Fonte retornou zero tarifas; arquivos anteriores preservados')
    evidencias=[]
    for ano in sorted(set(args.anos)):
        registros=consultar(INDGER_ID,{'DatReferenciaInformada':f'{ano}-12-01'},
                  ('NumCNPJ','SigAgente','CodMunicipioIBGE','DatReferenciaInformada','QtdUCAtiva'))
        if not registros:
            raise RuntimeError(f'Não há evidência municipal em dezembro/{ano}; escolha ano disponível')
        evidencias.extend(registros)
    vinculos=gerar_vinculos(evidencias)
    geo=json.loads(obter(GEO_URL))
    if {f['properties']['codarea'] for f in geo['features']} != {c for c,_ in CODIGOS_UF}:
        raise RuntimeError('Malha do IBGE não contém exatamente as 27 UFs esperadas')
    # Só grava depois que todas as consultas e a validação básica concluírem.
    salvar_csv(PASTA/'tarifas_aneel.csv',tarifas,tuple(k for k in tarifas[0] if k!='_id'))
    salvar_csv(PASTA/'evidencias_indger.csv',evidencias)
    salvar_csv(PASTA/'mapeamento_aneel.csv',vinculos)
    (PASTA/'brasil_ufs.geojson').write_text(json.dumps(geo),encoding='utf-8')
    manifesto={'origem':'ANEEL / IBGE; dados reais', 'coletado_em_utc':datetime.now(timezone.utc).isoformat(),
      'tarifas_resource_id':TARIFAS_ID,'tarifas_csv_original':CSV_OFICIAL,'filtro_api':FILTRO_API,
      'registros_tarifarios':len(tarifas),'indger_resource_id':INDGER_ID,'anos_mapeados':sorted(set(args.anos)),
      'registros_municipais':len(evidencias),'vinculos_uf':len(vinculos),'geojson_url':GEO_URL,
      'licenca_aneel':'Open Data Commons Open Database License (ODbL)',
      'nota':'Mapeamento derivado de municípios com UC ativa > 0, apenas no mês observado; cobertura parcial possível.',
      'sha256':{p.name:hash_arquivo(p) for p in (PASTA/'tarifas_aneel.csv',PASTA/'evidencias_indger.csv',PASTA/'mapeamento_aneel.csv',PASTA/'brasil_ufs.geojson')}}
    (PASTA/'fontes.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,KeyError,RuntimeError) as erro:
        raise SystemExit(f'Coleta não concluída: {erro}.')
