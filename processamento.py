"""Núcleo funcional: recebe valores e devolve novos valores; não lê arquivos."""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
import unicodedata
from typing import Mapping

# Tuplas e objetos frozen impedem alterações acidentais nos resultados.
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
CAMPOS = tuple(k for k, _ in FILTROS) + ('SigAgente','NumCNPJDistribuidora',
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

    @property
    def total(self) -> Decimal:
        return self.te + self.tusd

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

def texto(valor: object) -> str:
    """Compara rótulos ignorando acentos, caixa e espaços duplicados."""
    normal = unicodedata.normalize('NFKD', str(valor or '').strip())
    return ' '.join(''.join(c for c in normal if not unicodedata.combining(c)).casefold().split())

def normalizar_cnpj(valor: object) -> str:
    bruto = str(valor or '').strip()
    # Aceita CNPJ pontuado e zeros iniciais perdidos, mas não notação científica.
    if not re.fullmatch(r'[0-9./-]+', bruto):
        raise ValueError('CNPJ ausente ou em formato inválido; preserve-o como texto')
    digitos = re.sub(r'\D', '', bruto)
    if not 1 <= len(digitos) <= 14:
        raise ValueError('CNPJ deve ter até 14 algarismos')
    return digitos.zfill(14)

def numero(valor: object) -> Decimal:
    """Aceita 1.234,56, 1234.56 e ,00; ausente nunca vira zero."""
    s = str(valor).strip()
    if ',' in s:
        if not re.fullmatch(r'[+-]?(?:\d{1,3}(?:\.\d{3})*|\d*)?,\d+', s):
            raise ValueError(f'Número brasileiro inválido: {s!r}')
        s = s.replace('.', '').replace(',', '.')
    elif not re.fullmatch(r'[+-]?\d+(?:\.\d+)?', s):
        raise ValueError(f'Número inválido ou ausente: {s!r}')
    try:
        n = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError(f'Número inválido: {s!r}') from exc
    if not n.is_finite() or n < 0:
        raise ValueError('Tarifa deve ser finita e não negativa')
    return n

def data(valor: object) -> date:
    s = str(valor).strip()
    for formato in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(s, formato).date()
        except ValueError:
            pass
    raise ValueError(f'Data inválida ou ausente: {s!r}')

def comparavel(linha: Mapping[str, str]) -> bool:
    return all(texto(linha.get(campo)) == esperado for campo, esperado in FILTROS)

def normalizar(linha: Mapping[str, str]) -> Tarifa:
    unidade = texto(linha['DscUnidadeTerciaria']).replace(' ', '')
    fatores = {'mwh': Decimal(1000), 'r$/mwh': Decimal(1000),
               'kwh': Decimal(1), 'r$/kwh': Decimal(1)}
    if unidade not in fatores:
        raise ValueError('Unidade incompatível: apenas energia em MWh ou kWh; kW é demanda')
    inicio, fim = data(linha['DatInicioVigencia']), data(linha['DatFimVigencia'])
    if fim < inicio:
        raise ValueError('Fim da vigência anterior ao início')
    if not linha['SigAgente'].strip():
        raise ValueError('Distribuidora sem nome')
    return Tarifa(normalizar_cnpj(linha['NumCNPJDistribuidora']), linha['SigAgente'].strip(),
                  inicio, fim, numero(linha['VlrTE']) / fatores[unidade],
                  numero(linha['VlrTUSD']) / fatores[unidade], linha['DscREH'].strip())

def processar(linhas: tuple[Mapping[str, str], ...]) -> Processamento:
    """filter escolhe o perfil; map converte registros sem alterar a entrada."""
    if not linhas:
        return Processamento((), (), 0, 0)
    for linha in linhas:
        faltantes = set(CAMPOS) - set(linha)
        if faltantes:
            raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(sorted(faltantes)))
    selecionadas = tuple(filter(lambda par: comparavel(par[1]), enumerate(linhas, start=2)))

    def tentar(par):
        indice, linha = par
        try:
            return normalizar(linha)
        except ValueError as exc:
            return Problema(indice, str(exc))

    resultados = tuple(map(tentar, selecionadas))
    return Processamento(tuple(r for r in resultados if isinstance(r, Tarifa)),
                         tuple(r for r in resultados if isinstance(r, Problema)),
                         len(linhas), len(linhas) - len(selecionadas))

def normalizar_vinculos(linhas: tuple[Mapping[str, str], ...]) -> tuple[Vinculo, ...]:
    def converter(r):
        uf = r['UF'].strip().upper()
        inicio, fim = data(r['Inicio']), data(r['Fim'])
        if uf not in UFS or fim < inicio or not r['Fonte'].strip():
            raise ValueError('Mapeamento exige UF válida, período coerente e fonte')
        return Vinculo(normalizar_cnpj(r['CNPJ']), uf, inicio, fim, r['Fonte'].strip())
    try:
        return tuple(sorted(frozenset(map(converter, linhas)), key=lambda v: (v.cnpj,v.uf,v.inicio)))
    except KeyError as exc:
        raise ValueError(f'Coluna ausente no mapeamento: {exc}') from exc
