import csv
import io
import json
from pathlib import Path

def interpretar_csv(conteudo: bytes) -> tuple[dict[str,str], ...]:
    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = conteudo.decode('cp1252')
    cabecalho = texto.splitlines()[0] if texto.strip() else ''
    if not cabecalho:
        raise ValueError('CSV vazio')
    delimitador = ';' if cabecalho.count(';') > cabecalho.count(',') else ','
    leitor = csv.DictReader(io.StringIO(texto), delimiter=delimitador)
    nomes = tuple(c.strip() for c in (leitor.fieldnames or ()))
    if len(set(nomes)) != len(nomes):
        raise ValueError('CSV com colunas duplicadas')
    linhas = []
    for numero, r in enumerate(leitor, start=2):
        if None in r or any(v is None for v in r.values()):
            raise ValueError(f'CSV malformado na linha {numero}; confira o separador')
        linhas.append({k.strip():v.strip() for k,v in r.items()})
    return tuple(linhas)

def ler_csv(caminho: Path):
    return interpretar_csv(caminho.read_bytes())

def ler_json(caminho: Path):
    return json.loads(caminho.read_text(encoding='utf-8'))

def salvar_csv(caminho: Path, linhas, campos=None):
    linhas = tuple(linhas)
    if not linhas and campos is None:
        raise ValueError('Não é possível salvar CSV sem cabeçalho')
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + '.part')
    with temporario.open('w',encoding='utf-8-sig',newline='') as arquivo:
        writer=csv.DictWriter(arquivo,fieldnames=campos or tuple(linhas[0]),delimiter=';',extrasaction='ignore')
        writer.writeheader()
        writer.writerows(linhas)
    temporario.replace(caminho)
