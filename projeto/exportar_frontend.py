"""Exporta o núcleo funcional para a interface React, sem recalcular médias em JS."""
from pathlib import Path
import hashlib
import json
import math
from arquivos import ler_csv, ler_json
from processamento import processar, normalizar_vinculos, CODIGOS_UF, UFS
from analise import fotografia, resumir, ranking

RAIZ = Path(__file__).resolve().parent
NOMES = dict(zip(UFS, ('Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará',
    'Distrito Federal','Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul',
    'Minas Gerais','Pará','Paraíba','Paraná','Pernambuco','Piauí','Rio de Janeiro',
    'Rio Grande do Norte','Rio Grande do Sul','Rondônia','Roraima','Santa Catarina',
    'São Paulo','Sergipe','Tocantins')))

def projetar_mapa(geo):
    """Projeção Mercator para SVG. Geometrias reais do IBGE, sem redesenhar UFs."""
    def projetar(ponto):
        lon, lat = ponto[:2]
        return math.radians(lon), -math.log(math.tan(math.pi/4+math.radians(lat)/2))
    def aneis(feature):
        g=feature['geometry']
        if g['type']=='Polygon': return tuple(g['coordinates'])
        if g['type']=='MultiPolygon': return tuple(r for p in g['coordinates'] for r in p)
        raise ValueError('A malha deve conter apenas polígonos')
    pontos=tuple(projetar(p) for f in geo['features'] for r in aneis(f) for p in r)
    xmin,xmax=min(p[0] for p in pontos),max(p[0] for p in pontos)
    ymin,ymax=min(p[1] for p in pontos),max(p[1] for p in pontos)
    escala=min(560/(xmax-xmin),550/(ymax-ymin))
    dx=(640-(xmax-xmin)*escala)/2
    dy=(600-(ymax-ymin)*escala)/2
    def caminho(anel):
        coords=tuple(((x-xmin)*escala+dx,(y-ymin)*escala+dy) for x,y in map(projetar,anel))
        return 'M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in coords)+'Z'
    codigos=dict(CODIGOS_UF)
    return tuple({'uf':codigos[f['properties']['codarea']],
                  'path':''.join(map(caminho,aneis(f)))} for f in geo['features'])

def preparar(tarifas, vinculos, geo, manifesto):
    """Transformação pura: mesmas entradas produzem o mesmo conteúdo exportado."""
    resultado=processar(tarifas)
    vinculos=normalizar_vinculos(vinculos)
    datas=sorted({v.fim for v in vinculos if any(
        t.cnpj==v.cnpj and t.inicio<=v.fim<=t.fim for t in resultado.tarifas)})
    referencias=[]
    for dia in datas:
        foto=fotografia(resultado.tarifas,vinculos,dia)
        resumos=resumir(foto.itens)
        ordem=ranking(resumos)
        def estado(r):
            itens=tuple(sorted((i.tarifa for i in foto.itens if i.uf==r.uf),key=lambda t:t.total))
            return {'uf':r.uf,'nome':NOMES[r.uf],'quantidade':r.quantidade,
                'media':str(r.media) if r.media is not None else None,
                'minima':str(r.minima) if r.minima is not None else None,
                'maxima':str(r.maxima) if r.maxima is not None else None,
                'distribuidoras':[{'nome':t.agente,'cnpj':t.cnpj,'te':str(t.te),'tusd':str(t.tusd),
                    'total':str(t.total),'inicio':t.inicio.isoformat(),'fim':t.fim.isoformat(),
                    'resolucao':t.resolucao} for t in itens]}
        referencias.append({'data':dia.isoformat(),'ano':dia.year,
            'estados':list(map(estado,resumos)),'ranking':[r.uf for r in ordem],
            'cobertura':len(ordem),'distribuidoras':len({i.tarifa.cnpj for i in foto.itens}),
            'conflitos':list(foto.conflitos),'semMapeamento':list(foto.sem_mapeamento)})
    return {'fonte':'ANEEL','coleta':manifesto['coletado_em_utc'],
            'linhas':resultado.total_linhas,'foraPerfil':resultado.fora_recorte,
            'invalidas':len(resultado.problemas),'referencias':referencias,
            'mapa':projetar_mapa(geo),'hashesOriginais':manifesto['sha256']}

def main():
    pasta=RAIZ/'dados'
    manifesto=ler_json(pasta/'fontes.json')
    for nome,esperado in manifesto['sha256'].items():
        if hashlib.sha256((pasta/nome).read_bytes()).hexdigest()!=esperado:
            raise ValueError(f'Arquivo alterado desde a coleta: {nome}. Atualize o manifesto oficial antes de exportar.')
    payload=preparar(ler_csv(pasta/'tarifas_aneel.csv'),ler_csv(pasta/'mapeamento_aneel.csv'),
                    ler_json(pasta/'brasil_ufs.geojson'),manifesto)
    destino=RAIZ/'interface/src/data/painel.json'
    destino.parent.mkdir(parents=True,exist_ok=True)
    destino.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Exportadas {len(payload["referencias"])} referências oficiais e {len(payload["mapa"])} UFs.')

if __name__=='__main__':
    main()
