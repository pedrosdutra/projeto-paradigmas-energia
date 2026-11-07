import { useState } from 'react';
import { money, searchStates } from '../lib/format.mjs';

export default function Ranking({ reference, onSelect }) {
  const [query,setQuery]=useState('');
  const ordered=reference.ranking.map(uf=>reference.estados.find(s=>s.uf===uf));
  const filtered=searchStates(ordered,query);
  return <section aria-labelledby="ranking-heading">
    <div className="mb-6 flex flex-wrap items-end justify-between gap-5">
      <div><h2 id="ranking-heading" className="text-xl font-medium tracking-tight">Ranking das médias</h2>
        <p className="mt-2 text-xs text-subtle">Média simples · R$/kWh</p></div>
      <label className="text-xs text-secondary">Filtrar estado<input className="input-control mt-2 block" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Nome ou sigla" type="search" /></label>
    </div>
    <div className="overflow-x-auto"><table className="ranking-table w-full text-left text-sm">
      <caption className="sr-only">Ranking das tarifas médias, com quantidade de distribuidoras e intervalo de tarifas</caption>
      <thead><tr><th scope="col">Posição</th><th scope="col">Estado</th><th scope="col">Média / kWh</th><th scope="col">Distribuidoras</th><th scope="col">Menor tarifa</th><th scope="col">Maior tarifa</th></tr></thead>
      <tbody>{filtered.map(s=><tr key={s.uf}><td className="text-subtle">{String(ordered.indexOf(s)+1).padStart(2,'0')}</td>
        <th scope="row"><button onClick={()=>onSelect(s.uf)} className="text-left font-medium underline-offset-4 hover:underline">{s.nome}<span className="ml-3 text-xs font-normal text-subtle">{s.uf}</span></button></th>
        <td className="font-medium tabular-nums text-accent">{money(s.media)}</td><td className="tabular-nums text-secondary">{s.quantidade}</td>
        <td className="tabular-nums text-secondary">{money(s.minima)}</td><td className="tabular-nums text-secondary">{money(s.maxima)}</td></tr>)}</tbody>
    </table></div>
    {!filtered.length && <p className="py-10 text-center text-sm text-secondary" role="status">Nenhum estado encontrado. Tente outro nome ou sigla.</p>}
  </section>;
}
