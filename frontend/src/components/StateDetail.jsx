import { useState } from 'react';
import { money, decimal, dateLabel } from '../lib/format.mjs';

export default function StateDetail({ state, states, onSelect, date, rank }) {
  const [expanded,setExpanded]=useState(false);
  const shown=expanded ? state.distribuidoras : state.distribuidoras.slice(0,4);
  return <section aria-labelledby="state-heading" className="border-t border-line pt-7 lg:border-l lg:border-t-0 lg:pl-9 lg:pt-0">
    <div className="flex items-center justify-between gap-4">
      <label htmlFor="state-select" className="eyebrow">Estado em detalhe</label>
      <select id="state-select" value={state.uf} onChange={e=>{onSelect(e.target.value);setExpanded(false);}}
        className="select-control max-w-[190px] text-xs" aria-label="Selecionar estado">
        {states.map(s=><option key={s.uf} value={s.uf}>{s.nome} ({s.uf})</option>)}
      </select>
    </div>
    <div className="mb-7 mt-6 flex items-baseline justify-between gap-3">
      <h2 id="state-heading" className="text-[27px] font-medium leading-tight tracking-[-.035em]">{state.nome}</h2>
      <span className="text-xs text-subtle">{state.uf}</span>
    </div>
    <div aria-live="polite" aria-atomic="true">
      <p className="text-xs text-secondary">Média das distribuidoras observadas</p>
      <p className="mt-2 text-[34px] font-medium leading-none tracking-[-.055em] tabular-nums">{money(state.media)}<span className="ml-2 text-[12px] font-normal tracking-normal text-subtle">/ kWh</span></p>
      <p className="mt-3 text-xs text-secondary">{state.quantidade} {state.quantidade===1?'distribuidora':'distribuidoras'}{rank>0 ? ` · ${rank}ª posição por maior média` : ''}</p>
    </div>
    <div className="my-6 grid grid-cols-2 border-y border-line py-4 text-xs">
      <div><p className="mb-1.5 text-subtle">Menor tarifa</p><p className="font-medium tabular-nums">{money(state.minima)}</p></div>
      <div><p className="mb-1.5 text-subtle">Maior tarifa</p><p className="font-medium tabular-nums">{money(state.maxima)}</p></div>
    </div>
    <div className="flex items-center justify-between"><h3 className="text-sm font-medium">Distribuidoras</h3><span className="text-[10px] text-subtle">R$/kWh</span></div>
    {shown.length ? <div className="mt-3 overflow-x-auto">
      <table className="detail-table w-full text-left text-xs">
        <caption className="sr-only">TE, TUSD e tarifa total das distribuidoras em {state.nome}</caption>
        <thead><tr><th scope="col">Agente</th><th scope="col">TE</th><th scope="col">TUSD</th><th scope="col">Total</th></tr></thead>
        <tbody>{shown.map(d=><tr key={d.cnpj}><th scope="row" className="max-w-32 break-words font-medium">{d.nome}</th>
          <td>{decimal(d.te)}</td><td>{decimal(d.tusd)}</td><td className="font-medium">{decimal(d.total)}</td></tr>)}</tbody>
      </table>
    </div> : <p className="my-6 text-sm text-secondary">Sem tarifa comparável nesta referência.</p>}
    {state.distribuidoras.length>4 && <button onClick={()=>setExpanded(v=>!v)} className="mt-3 text-xs font-medium text-accent underline-offset-4 hover:underline" aria-expanded={expanded}>
      {expanded ? 'Mostrar menos' : `Ver as ${state.quantidade} distribuidoras`}</button>}
    <details className="mt-6 border-t border-line pt-4">
      <summary className="cursor-pointer text-xs font-medium text-body">Vigências e resoluções</summary>
      <div className="max-h-64 overflow-y-auto pr-2">{state.distribuidoras.map(d=><article key={d.cnpj} className="border-b border-line py-4 text-xs leading-relaxed">
        <h4 className="font-semibold">{d.nome}</h4><p className="mt-1 text-secondary">CNPJ {d.cnpj}</p>
        <p className="mt-1">{dateLabel(d.inicio)} — {dateLabel(d.fim)}</p><p className="mt-2 text-secondary">{d.resolucao}</p>
      </article>)}</div>
    </details>
    <p className="mt-5 text-[11px] text-subtle">Vigência consultada: {dateLabel(date)}.</p>
  </section>;
}
