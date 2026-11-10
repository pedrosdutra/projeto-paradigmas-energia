from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from itertools import filterfalse
from operator import itemgetter
import re
import unicodedata

from funcy import raiser
from toolz import excepts

UFS = ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
       'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO')
CODIGOS_UF = (('11','RO'),('12','AC'),('13','AM'),('14','RR'),('15','PA'),
              ('16','AP'),('17','TO'),('21','MA'),('22','PI'),('23','CE'),
              ('24','RN'),('25','PB'),('26','PE'),('27','AL'),('28','SE'),
              ('29','BA'),('31','MG'),('32','ES'),('33','RJ'),('35','SP'),
              ('41','PR'),('42','SC'),('43','RS'),('50','MS'),('51','MT'),
              ('52','GO'),('53','DF'))
FILTROS = (('DscBaseTarifaria','tarifa de aplicacao'), ('DscSubGrupo','b1'),
           ('DscModalidadeTarifaria','convencional'), ('DscClasse','residencial'),
           ('DscSubClasse','residencial'), ('DscDetalhe','nao se aplica'),
           ('NomPostoTarifario','nao se aplica'), ('SigAgenteAcessante','nao se aplica'))
CAMPOS = tuple(map(itemgetter(0), FILTROS)) + ('SigAgente','NumCNPJDistribuidora',
    'DatInicioVigencia','DatFimVigencia','DscUnidadeTerciaria','VlrTE','VlrTUSD','DscREH')

@dataclass(frozen=True)
class Tarifa:
    cnpj: str
    agente: str
    inicio: date
    fim: date
    te: Decimal  # Sempre em R$/kWh depois da normalização.
    tusd: Decimal
    resolucao: str

    total = property(lambda self: self.te + self.tusd)

@dataclass(frozen=True)
class Vinculo:
    cnpj: str
    uf: str
    inicio: date
    fim: date
    fonte: str

@dataclass(frozen=True)
class Problema:
    linha: int
    motivo: str

@dataclass(frozen=True)
class Processamento:
    tarifas: tuple[Tarifa, ...]
    problemas: tuple[Problema, ...]
    total_linhas: int
    fora_recorte: int

falhar = lambda mensagem: raiser(ValueError, mensagem)()
sem_acentos = lambda valor: ''.join(filterfalse(unicodedata.combining, unicodedata.normalize('NFKD', valor)))
texto = lambda valor: ' '.join(sem_acentos(str(valor or '').strip()).casefold().split())

digitos_cnpj = lambda bruto: re.sub(r'\D', '', bruto)
completar_cnpj = lambda digitos: (
    digitos.zfill(14) if 1 <= len(digitos) <= 14 else falhar('CNPJ deve ter até 14 algarismos')
)
limpar_cnpj = lambda bruto: (
    completar_cnpj(digitos_cnpj(bruto)) if re.fullmatch(r'[0-9./-]+', bruto)
    else falhar('CNPJ ausente ou em formato inválido; preserve-o como texto')
)
normalizar_cnpj = lambda valor: limpar_cnpj(str(valor or '').strip())

decimal_brasileiro = lambda s: (
    Decimal(s.replace('.', '').replace(',', '.'))
    if re.fullmatch(r'[+-]?(?:\d{1,3}(?:\.\d{3})*|\d*)?,\d+', s)
    else falhar(f'Número brasileiro inválido: {s!r}')
)
decimal_simples = lambda s: (
    Decimal(s) if re.fullmatch(r'[+-]?\d+(?:\.\d+)?', s)
    else falhar(f'Número inválido ou ausente: {s!r}')
)
ler_decimal = lambda s: decimal_brasileiro(s) if ',' in s else decimal_simples(s)
nao_negativo = lambda n: n if n >= 0 else falhar('Tarifa deve ser finita e não negativa')
numero = lambda valor: nao_negativo(ler_decimal(str(valor).strip()))
data = lambda valor: datetime.strptime(
    str(valor).strip(), '%d/%m/%Y' if '/' in str(valor) else '%Y-%m-%d'
).date()

comparavel = lambda linha: all(map(lambda par: texto(linha.get(par[0])) == par[1], FILTROS))
FATORES = {'mwh': 1000, 'r$/mwh': 1000, 'kwh': 1, 'r$/kwh': 1}
fator_unidade = lambda unidade: (
    FATORES[unidade] if unidade in FATORES else falhar('Unidade incompatível: use MWh ou kWh')
)
criar_tarifa = lambda linha, inicio, fim, fator: (
    falhar('Fim da vigência anterior ao início') if fim < inicio
    else falhar('Distribuidora sem nome') if not linha['SigAgente'].strip()
    else Tarifa(
        normalizar_cnpj(linha['NumCNPJDistribuidora']), linha['SigAgente'].strip(), inicio, fim,
        numero(linha['VlrTE']) / fator, numero(linha['VlrTUSD']) / fator, linha['DscREH'].strip()
    )
)
normalizar = lambda linha: criar_tarifa(
    linha, data(linha['DatInicioVigencia']), data(linha['DatFimVigencia']),
    fator_unidade(texto(linha['DscUnidadeTerciaria']).replace(' ', ''))
)
tentar = lambda par: excepts(ValueError, normalizar, lambda erro: Problema(par[0], str(erro)))(par[1])
selecionar = lambda linhas: filter(lambda par: comparavel(par[1]), enumerate(linhas, start=2))
organizar = lambda resultados, quantidade: Processamento(
    tuple(filter(lambda r: isinstance(r, Tarifa), resultados)),
    tuple(filter(lambda r: isinstance(r, Problema), resultados)),
    quantidade, quantidade - len(resultados)
)
colunas_ausentes = lambda linhas: next(filter(bool, map(lambda r: set(CAMPOS).difference(r), linhas)), ())
processar_com_campos = lambda linhas, faltantes: (
    falhar('Colunas obrigatórias ausentes: ' + ', '.join(sorted(faltantes))) if faltantes
    else organizar(tuple(map(tentar, selecionar(linhas))), len(linhas))
)
processar = lambda linhas: processar_com_campos(linhas, colunas_ausentes(linhas))

validar_vinculo = lambda v: (
    v if v.uf in UFS and v.fim >= v.inicio and v.fonte
    else falhar('Mapeamento exige UF válida, período coerente e fonte')
)
converter_vinculo = lambda r: validar_vinculo(Vinculo(
    normalizar_cnpj(r['CNPJ']), r['UF'].strip().upper(), data(r['Inicio']), data(r['Fim']), r['Fonte'].strip()
))
ler_vinculo = excepts(KeyError, converter_vinculo, lambda erro: falhar(f'Coluna ausente no mapeamento: {erro}'))
normalizar_vinculos = lambda linhas: tuple(sorted(
    frozenset(map(ler_vinculo, linhas)), key=lambda v: (v.cnpj, v.uf, v.inicio)
))
