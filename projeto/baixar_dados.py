"""Coleta reproduzível. Rede e gravação ficam separadas do núcleo funcional."""
import argparse
import calendar
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from itertools import chain, takewhile
from operator import itemgetter

import requests
from funcy import raiser
from toolz import do, iterate
from arquivos import salvar_csv
from processamento import CODIGOS_UF, normalizar_cnpj, numero, falhar

BASE = 'https://dadosabertos.aneel.gov.br/api/3/action/'
TARIFAS_ID = 'fcf2906c-7c32-4b9b-a637-054e7a5234f4'
INDGER_ID = 'fd10c9d4-cb76-4020-a322-e79afb13eaf7'
CSV_OFICIAL = 'https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv'
GEO_URL = 'https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=UF'
FILTRO_API = {'DscSubGrupo':'B1','DscModalidadeTarifaria':'Convencional',
              'DscClasse':'Residencial','DscSubClasse':'Residencial',
              'DscBaseTarifaria':'Tarifa de Aplicação'}
PASTA = Path(__file__).resolve().parent / 'dados'

descompactar = lambda conteudo: gzip.decompress(conteudo) if conteudo.startswith(b'\x1f\x8b') else conteudo
obter = lambda url: descompactar(do(lambda r: r.raise_for_status(), requests.get(
    url, headers={'User-Agent': 'ProjetoAcademicoTarifas/1.0'}, timeout=90
)).content)
erro_coleta = lambda mensagem: raiser(RuntimeError, mensagem)()
resultado_api = lambda pagina: (
    pagina['result'] if pagina.get('success') else erro_coleta(f'Consulta recusada: {pagina.get("error")}')
)
pedir = lambda recurso, filtros, campos, offset: resultado_api(json.loads(obter(
    BASE + 'datastore_search?' + urlencode({
        'resource_id': recurso, 'filters': json.dumps(filtros), 'limit': 5000, 'offset': offset,
        'sort': '_id asc', **({'fields': ','.join(campos)} if campos else {})
    })
)))
# O próximo deslocamento acompanha a quantidade efetivamente recebida da ANEEL.
pagina = lambda resposta, offset, total: (
    erro_coleta('A base mudou durante a coleta. Execute novamente.')
    if total is not None and resposta['total'] != total
    else erro_coleta('Paginação incompleta: a coleta foi interrompida')
    if not resposta['records'] and offset < resposta['total']
    else (offset + len(resposta['records']), resposta['total'], resposta['records'])
)
paginar = lambda buscar: iterate(
    lambda anterior: pagina(buscar(anterior[0]), anterior[0], anterior[1])
    if anterior[0] < anterior[1] else None,
    pagina(buscar(0), 0, None)
)
consultar = lambda recurso, filtros, campos=None: tuple(chain.from_iterable(map(
    itemgetter(2), takewhile(lambda p: p is not None, paginar(lambda offset: pedir(recurso, filtros, campos, offset)))
)))

SIGLAS = dict(CODIGOS_UF)
FONTE_INDGER = 'https://dadosabertos.aneel.gov.br/dataset/indger-indicadores-gerenciais-da-distribuicao/resource/' + INDGER_ID
uf_municipio = lambda codigo: (
    SIGLAS[codigo[:2]] if len(codigo) == 7 and codigo.isdigit() and codigo[:2] in SIGLAS
    else falhar(f'Código de município inválido: {codigo}')
)
periodo = lambda dia: (
    dia.replace(day=1).isoformat(), dia.replace(day=calendar.monthrange(dia.year, dia.month)[1]).isoformat()
)
vinculo = lambda r: (
    normalizar_cnpj(r['NumCNPJ']), uf_municipio(str(r['CodMunicipioIBGE']).strip()),
    *periodo(date.fromisoformat(r['DatReferenciaInformada'])), FONTE_INDGER
)
CAMPOS_VINCULO = ('CNPJ', 'UF', 'Inicio', 'Fim', 'Fonte')
gerar_vinculos = lambda registros: tuple(map(
    lambda v: dict(zip(CAMPOS_VINCULO, v)),
    sorted(set(map(vinculo, filter(lambda r: numero(r['QtdUCAtiva']) > 0, registros))))
))
evidencia_ano = lambda ano: consultar(
    INDGER_ID, {'DatReferenciaInformada': f'{ano}-12-01'},
    ('NumCNPJ', 'SigAgente', 'CodMunicipioIBGE', 'DatReferenciaInformada', 'QtdUCAtiva')
) or erro_coleta(f'Não há evidência municipal em dezembro/{ano}; escolha ano disponível')
hash_arquivo = lambda caminho: hashlib.sha256(caminho.read_bytes()).hexdigest()
ARQUIVOS = ('tarifas_aneel.csv', 'evidencias_indger.csv', 'mapeamento_aneel.csv', 'brasil_ufs.geojson')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anos', type=int, nargs='+', default=[2024, 2025], help='Anos de referência em dezembro')
    anos = sorted(set(parser.parse_args().anos))
    try:
        tarifas = consultar(TARIFAS_ID, FILTRO_API)
        if not tarifas:
            raise RuntimeError('Fonte retornou zero tarifas; arquivos anteriores preservados')
        evidencias = tuple(chain.from_iterable(map(evidencia_ano, anos)))
        vinculos = gerar_vinculos(evidencias)
        geo = json.loads(obter(GEO_URL))
        if set(map(lambda f: f['properties']['codarea'], geo['features'])) != set(SIGLAS):
            raise ValueError('Malha do IBGE não contém exatamente as 27 UFs esperadas')
        PASTA.mkdir(exist_ok=True)
        salvar_csv(PASTA / ARQUIVOS[0], tarifas, tuple(filter(lambda k: k != '_id', tarifas[0])))
        salvar_csv(PASTA / ARQUIVOS[1], evidencias)
        salvar_csv(PASTA / ARQUIVOS[2], vinculos)
        (PASTA / ARQUIVOS[3]).write_text(json.dumps(geo), encoding='utf-8')
        manifesto = {
            'origem': 'ANEEL / IBGE; dados reais', 'coletado_em_utc': datetime.now(timezone.utc).isoformat(),
            'tarifas_resource_id': TARIFAS_ID, 'tarifas_csv_original': CSV_OFICIAL, 'filtro_api': FILTRO_API,
            'registros_tarifarios': len(tarifas), 'indger_resource_id': INDGER_ID, 'anos_mapeados': anos,
            'registros_municipais': len(evidencias), 'vinculos_uf': len(vinculos), 'geojson_url': GEO_URL,
            'licenca_aneel': 'Open Data Commons Open Database License (ODbL)',
            'nota': 'Mapeamento derivado de municípios com UC ativa > 0, apenas no mês observado; cobertura parcial possível.',
            'sha256': dict(map(lambda nome: (nome, hash_arquivo(PASTA / nome)), ARQUIVOS))
        }
        (PASTA/'fontes.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding='utf-8')
    except (OSError, ValueError, KeyError, RuntimeError) as erro:
        raise SystemExit(f'Coleta não concluída: {erro}.')
