from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from functools import reduce
from itertools import chain, filterfalse, groupby, starmap
from operator import attrgetter, itemgetter
from processamento import Tarifa, Vinculo, UFS

@dataclass(frozen=True)
class ItemUF:
    uf: str
    tarifa: Tarifa

@dataclass(frozen=True)
class Fotografia:
    itens: tuple[ItemUF, ...]
    conflitos: tuple[str, ...]
    sem_mapeamento: tuple[str, ...]
    distribuidoras_vigentes: int

@dataclass(frozen=True)
class ResumoUF:
    uf: str
    quantidade: int
    media: Decimal | None
    minima: Decimal | None
    maxima: Decimal | None

somar_tarifa = lambda acumulado, tarifa: (acumulado[0] + tarifa, acumulado[1] + 1)
dividir = lambda soma, quantidade: soma / quantidade if quantidade else None
media = lambda valores: dividir(*reduce(somar_tarifa, valores, (Decimal(0), 0)))

vigente = lambda registro, dia: registro.inicio <= dia <= registro.fim
cnpj = attrgetter('cnpj')
componentes = attrgetter('te', 'tusd')
representante = lambda grupo: (
    max(grupo, key=attrgetter('inicio', 'fim', 'resolucao', 'agente'))
    if len(set(map(componentes, grupo))) == 1 else None
)
escolher = lambda chave, grupo: (chave, representante(tuple(grupo)))
agrupar = lambda tarifas: tuple(starmap(escolher, groupby(sorted(tarifas, key=cnpj), key=cnpj)))

ufs_atendidas = lambda tarifa, vinculos: sorted(set(map(
    attrgetter('uf'), filter(lambda v: v.cnpj == tarifa.cnpj, vinculos)
)))
vincular = lambda tarifa, vinculos: tuple(map(lambda uf: ItemUF(uf, tarifa), ufs_atendidas(tarifa, vinculos)))
montar_foto = lambda grupos, itens, validas: Fotografia(
    itens,
    tuple(map(itemgetter(0), filter(lambda par: par[1] is None, grupos))),
    tuple(filterfalse(cnpjs_atendidos(itens).__contains__, map(cnpj, validas))),
    len(grupos)
)
cnpjs_atendidos = lambda itens: frozenset(map(attrgetter('tarifa.cnpj'), itens))
juntar_tarifas = lambda grupos, vinculos, validas: montar_foto(
    grupos, tuple(chain.from_iterable(map(lambda t: vincular(t, vinculos), validas))), validas
)
associar = lambda grupos, vinculos: juntar_tarifas(
    grupos, vinculos, tuple(filter(lambda t: t is not None, map(itemgetter(1), grupos)))
)
fotografia = lambda tarifas, vinculos, referencia: associar(
    agrupar(filter(lambda t: vigente(t, referencia), tarifas)),
    tuple(filter(lambda v: vigente(v, referencia), vinculos))
)

totais_unicos = lambda itens: tuple(dict(map(lambda i: (i.tarifa.cnpj, i.tarifa.total), itens)).values())
resumo_uf = lambda uf, valores: ResumoUF(
    uf, len(valores), media(valores), min(valores, default=None), max(valores, default=None)
)
resumir = lambda itens: tuple(map(
    lambda uf: resumo_uf(uf, totais_unicos(filter(lambda i: i.uf == uf, itens))), UFS
))
com_media = lambda estado: estado.media is not None
ranking = lambda resumos: tuple(sorted(filter(com_media, resumos), key=lambda r: (-r.media, r.uf)))
diferenca = lambda a, b: abs(a - b).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
diferencas_por_uf = lambda estado, resumos: dict(map(
    lambda outro: (outro.uf, diferenca(estado.media, outro.media)), filter(com_media, resumos)
)) if com_media(estado) else {}
