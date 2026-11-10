from pathlib import Path
import hashlib
import json
import math
from itertools import chain
from operator import attrgetter
from arquivos import ler_csv, ler_json
from processamento import processar, normalizar_vinculos, CODIGOS_UF, UFS, falhar
from analise import fotografia, resumir, ranking, diferencas_por_uf

RAIZ = Path(__file__).resolve().parent
NOMES = dict(zip(UFS, ('Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará',
    'Distrito Federal','Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul',
    'Minas Gerais','Pará','Paraíba','Paraná','Pernambuco','Piauí','Rio de Janeiro',
    'Rio Grande do Norte','Rio Grande do Sul','Rondônia','Roraima','Santa Catarina',
    'São Paulo','Sergipe','Tocantins')))

projetar = lambda ponto: (
    math.radians(ponto[0]), -math.log(math.tan(math.pi / 4 + math.radians(ponto[1]) / 2))
)
aneis = lambda geo: (
    geo['coordinates'] if geo['type'] == 'Polygon'
    else tuple(chain.from_iterable(geo['coordinates'])) if geo['type'] == 'MultiPolygon'
    else falhar('A malha deve conter apenas polígonos')
)
aneis_da_uf = lambda uf: aneis(uf['geometry'])
pontos_do_mapa = lambda ufs: map(projetar, chain.from_iterable(chain.from_iterable(map(aneis_da_uf, ufs))))
extremos = lambda valores: (min(valores), max(valores))
limites = lambda pontos: tuple(map(extremos, zip(*pontos)))
ajustar = lambda x, y, xmin, ymin, escala, dx, dy: (
    f'{(x-xmin)*escala+dx:.2f},{(y-ymin)*escala+dy:.2f}'
)
transformacao = lambda xmin, ymin, largura, altura, escala: (
    lambda ponto: ajustar(*projetar(ponto), xmin, ymin, escala, (640-largura*escala)/2, (600-altura*escala)/2)
)
escala_mapa = lambda xmin, ymin, largura, altura: transformacao(
    xmin, ymin, largura, altura, min(560/largura, 550/altura)
)
enquadrar = lambda xs, ys: escala_mapa(xs[0], ys[0], xs[1]-xs[0], ys[1]-ys[0])
caminho = lambda anel, coordenada: 'M' + 'L'.join(map(coordenada, anel)) + 'Z'
SIGLAS = dict(CODIGOS_UF)
desenhar = lambda uf, coordenada: {
    'uf': SIGLAS[uf['properties']['codarea']],
    'path': ''.join(map(lambda anel: caminho(anel, coordenada), aneis_da_uf(uf)))
}
desenhar_ufs = lambda ufs, coordenada: tuple(map(lambda uf: desenhar(uf, coordenada), ufs))
projetar_mapa = lambda geo: desenhar_ufs(geo['features'], enquadrar(*limites(pontos_do_mapa(geo['features']))))

descricao_tarifa = lambda t: {
    'nome': t.agente, 'cnpj': t.cnpj, 'te': str(t.te), 'tusd': str(t.tusd), 'total': str(t.total),
    'inicio': t.inicio.isoformat(), 'fim': t.fim.isoformat(), 'resolucao': t.resolucao
}
texto_decimal = lambda valor: None if valor is None else str(valor)
tarifas_da_uf = lambda uf, itens: sorted(
    map(attrgetter('tarifa'), filter(lambda i: i.uf == uf, itens)), key=attrgetter('total')
)
estado = lambda r, itens, resumos: {
    'uf': r.uf, 'nome': NOMES[r.uf], 'quantidade': r.quantidade, 'media': texto_decimal(r.media),
    'diferencas': dict(map(lambda par: (par[0], str(par[1])), diferencas_por_uf(r, resumos).items())),
    'minima': texto_decimal(r.minima), 'maxima': texto_decimal(r.maxima),
    'distribuidoras': list(map(descricao_tarifa, tarifas_da_uf(r.uf, itens)))
}
referencia = lambda dia, foto, resumos: {
    'data': dia.isoformat(), 'ano': dia.year,
    'estados': list(map(lambda r: estado(r, foto.itens, resumos), resumos)),
    'ranking': list(map(attrgetter('uf'), ranking(resumos))),
    'cobertura': sum(map(lambda r: r.media is not None, resumos)),
    'distribuidoras': len(set(map(attrgetter('tarifa.cnpj'), foto.itens))),
    'conflitos': list(foto.conflitos), 'semMapeamento': list(foto.sem_mapeamento)
}
resumir_foto = lambda dia, foto: referencia(dia, foto, resumir(foto.itens))
tem_tarifa = lambda v, tarifas: any(map(lambda t: t.cnpj == v.cnpj and t.inicio <= v.fim <= t.fim, tarifas))
datas_referencia = lambda tarifas, vinculos: sorted(set(map(
    attrgetter('fim'), filter(lambda v: tem_tarifa(v, tarifas), vinculos)
)))
referencias = lambda tarifas, vinculos: list(map(
    lambda dia: resumir_foto(dia, fotografia(tarifas, vinculos, dia)), datas_referencia(tarifas, vinculos)
))
painel = lambda resultado, vinculos, geo, manifesto: {
    'fonte': 'ANEEL', 'coleta': manifesto['coletado_em_utc'],
    'linhas': resultado.total_linhas, 'foraPerfil': resultado.fora_recorte,
    'invalidas': len(resultado.problemas), 'referencias': referencias(resultado.tarifas, vinculos),
    'mapa': projetar_mapa(geo), 'hashesOriginais': manifesto['sha256']
}
preparar = lambda tarifas, vinculos, geo, manifesto: painel(
    processar(tarifas), normalizar_vinculos(vinculos), geo, manifesto
)
PASTA = RAIZ / 'dados'
DESTINO = RAIZ / 'interface/src/data/painel.json'
alterado = lambda par: hashlib.sha256((PASTA / par[0]).read_bytes()).hexdigest() != par[1]
conferir = lambda manifesto, divergente: (
    falhar(f'Arquivo alterado desde a coleta: {divergente[0]}') if divergente else manifesto
)
manifesto_verificado = lambda m: conferir(m, next(filter(alterado, m['sha256'].items()), None))
carregar = lambda manifesto: preparar(
    ler_csv(PASTA/'tarifas_aneel.csv'), ler_csv(PASTA/'mapeamento_aneel.csv'),
    ler_json(PASTA/'brasil_ufs.geojson'), manifesto
)
if __name__ == '__main__':
    dados = carregar(manifesto_verificado(ler_json(PASTA/'fontes.json')))
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps(dados, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
