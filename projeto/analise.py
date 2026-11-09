from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from functools import reduce
from itertools import groupby
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

def media(valores: tuple[Decimal, ...]) -> Decimal | None:
    """reduce acumula soma e contagem; ausência permanece None, nunca zero."""
    soma, n = reduce(lambda acc, x: (acc[0] + x, acc[1] + 1), valores, (Decimal(0), 0))
    return soma / n if n else None

def fotografia(tarifas: tuple[Tarifa, ...], vinculos: tuple[Vinculo, ...], referencia: date) -> Fotografia:
    vigentes = tuple(filter(lambda t: t.inicio <= referencia <= t.fim, tarifas))
    grupos = tuple((cnpj, tuple(g)) for cnpj, g in groupby(sorted(vigentes, key=lambda t:t.cnpj), key=lambda t:t.cnpj))
    def escolher(par):
        cnpj, grupo = par
        # Repetições idênticas e rótulos diferentes com mesmos componentes não pesam mais.
        componentes = frozenset((t.te, t.tusd) for t in grupo)
        if len(componentes) != 1:
            return cnpj, None
        return cnpj, max(grupo, key=lambda t:(t.inicio,t.fim,t.resolucao,t.agente))
    escolhidas = tuple(map(escolher, grupos))
    validas = tuple(t for _, t in escolhidas if t is not None)
    def ufs(t):
        return tuple(sorted(frozenset(v.uf for v in vinculos
                          if v.cnpj == t.cnpj and v.inicio <= referencia <= v.fim)))
    itens = tuple(ItemUF(uf,t) for t in validas for uf in ufs(t))
    return Fotografia(itens, tuple(c for c,t in escolhidas if t is None),
                      tuple(t.cnpj for t in validas if not ufs(t)), len(grupos))

def resumir(itens: tuple[ItemUF, ...]) -> tuple[ResumoUF, ...]:
    def por_uf(uf):
        registros = tuple(filter(lambda item:item.uf == uf, itens))
        valores = tuple(t.total for t in {i.tarifa.cnpj:i.tarifa for i in registros}.values())
        return ResumoUF(uf,len(valores),media(valores),min(valores) if valores else None,
                        max(valores) if valores else None)
    return tuple(map(por_uf, UFS))

def ranking(resumos: tuple[ResumoUF, ...]) -> tuple[ResumoUF, ...]:
    return tuple(sorted(filter(lambda r:r.media is not None,resumos), key=lambda r:(-r.media,r.uf)))

def diferencas_por_uf(estado: ResumoUF, resumos: tuple[ResumoUF, ...]) -> dict[str, Decimal]:
    """Compara as médias da mesma data e arredonda só a diferença final."""
    if estado.media is None:
        return {}
    return {
        outro.uf: abs(estado.media - outro.media).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        for outro in resumos if outro.media is not None
    }
