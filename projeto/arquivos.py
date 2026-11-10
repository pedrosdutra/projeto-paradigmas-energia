import csv
import io
import json
from itertools import chain
from uuid import uuid4

from toolz import do, excepts
from processamento import falhar

decodificar = lambda conteudo: excepts(
    UnicodeDecodeError, lambda: conteudo.decode('utf-8-sig'), lambda erro: conteudo.decode('cp1252')
)()
separador = lambda cabecalho: ';' if cabecalho.count(';') > cabecalho.count(',') else ','
limpar_linha = lambda par: (
    falhar(f'CSV malformado na linha {par[0]}; confira o separador')
    if None in par[1] or None in par[1].values()
    else dict(map(lambda campo: (campo[0].strip(), campo[1].strip()), par[1].items()))
)
ler_registros = lambda leitor, nomes: (
    falhar('CSV com colunas duplicadas') if len(set(nomes)) != len(nomes)
    else tuple(map(limpar_linha, enumerate(leitor, start=2)))
)
interpretar_leitor = lambda leitor: ler_registros(leitor, tuple(map(str.strip, leitor.fieldnames or ())))
interpretar_texto = lambda texto: (
    interpretar_leitor(csv.DictReader(io.StringIO(texto), delimiter=separador(texto.splitlines()[0])))
    if texto.strip() else falhar('CSV vazio')
)
interpretar_csv = lambda conteudo: interpretar_texto(decodificar(conteudo))
ler_csv = lambda caminho: interpretar_csv(caminho.read_bytes())
ler_json = lambda caminho: json.loads(caminho.read_text(encoding='utf-8'))

linhas_csv = lambda linhas, campos: chain((dict(zip(campos, campos)),), linhas)
preencher_csv = lambda memoria, linhas, campos: csv.DictWriter(
    memoria, fieldnames=campos, delimiter=';', extrasaction='ignore'
).writerows(linhas_csv(linhas, campos))
conteudo_csv = lambda linhas, campos: do(
    lambda memoria: preencher_csv(memoria, linhas, campos), io.StringIO(newline='')
).getvalue().encode('utf-8-sig')
publicar_csv = lambda destino, temporario, conteudo: do(
    lambda arquivo: arquivo.write_bytes(conteudo), temporario
).replace(destino)
gravar_csv = lambda destino, linhas, campos: publicar_csv(
    destino, destino.with_name(f'{destino.name}.{uuid4().hex}.part'), conteudo_csv(linhas, campos)
)
preparar_csv = lambda caminho, linhas, campos: (
    gravar_csv(do(lambda p: p.parent.mkdir(parents=True, exist_ok=True), caminho),
               linhas, campos if campos is not None else tuple(linhas[0]))
    if linhas or campos is not None else falhar('Não é possível salvar CSV sem cabeçalho')
)
salvar_csv = lambda caminho, linhas, campos=None: preparar_csv(caminho, tuple(linhas), campos)
