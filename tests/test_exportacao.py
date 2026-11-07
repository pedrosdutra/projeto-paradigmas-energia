"""Integração entre a fonte oficial, o núcleo funcional e o snapshot React."""
import hashlib
import json
from pathlib import Path
from arquivos import ler_csv, ler_json
from exportar_frontend import preparar

RAIZ = Path(__file__).resolve().parents[1]


def test_snapshot_corresponde_ao_calculo_python_e_fontes_incluidas():
    pasta = RAIZ / 'dados'
    manifesto = ler_json(pasta / 'fontes.json')
    for nome, esperado in manifesto['sha256'].items():
        assert hashlib.sha256((pasta / nome).read_bytes()).hexdigest() == esperado
    resultado = preparar(ler_csv(pasta / 'tarifas_aneel.csv'),
                         ler_csv(pasta / 'mapeamento_aneel.csv'),
                         ler_json(pasta / 'brasil_ufs.geojson'), manifesto)
    salvo = ler_json(RAIZ / 'frontend/src/data/painel.json')
    assert json.loads(json.dumps(resultado)) == salvo
    assert salvo['fonte'] == 'ANEEL'
    assert len(salvo['mapa']) == 27
    assert {r['ano'] for r in salvo['referencias']} == {2024, 2025}


def test_painel_compilado_e_autocontido():
    html = (RAIZ / 'frontend/dist/painel.html').read_text(encoding='utf-8')
    assert '<div id="root"></div>' in html
    assert '<script type="module">' in html
    assert 'src="./assets/' not in html
    assert 'href="./assets/' not in html
    checksum = hashlib.sha256((RAIZ / 'frontend/src/data/painel.json').read_bytes()).hexdigest()
    assert f'<meta name="dados-sha256" content="{checksum}">' in html
