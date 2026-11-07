import { useState } from 'react';
import { decimal, money, palette, tariffColor } from '../lib/format.mjs';

export default function MapView({ states, geometry, selected, onSelect }) {
  const [hovered,setHovered]=useState(null);
  const valid=states.filter(s=>s.media!=null).map(s=>Number(s.media));
  const min=valid.length ? Math.min(...valid) : 0;
  const max=valid.length ? Math.max(...valid) : 0;
  const tooltip=states.find(s=>s.uf===hovered);
  return <section aria-labelledby="map-title" className="min-w-0 lg:pr-10">
    <div className="flex flex-wrap items-baseline justify-between gap-2">
      <h2 id="map-title" className="text-[15px] font-semibold tracking-tight">Panorama por estado</h2>
      <span className="text-xs text-secondary">TE + TUSD · R$/kWh</span>
    </div>
    <div className="map-stage relative">
      <svg viewBox="0 0 640 600" className="map-svg" role="group" aria-labelledby="map-title map-desc">
        <desc id="map-desc">Mapa do Brasil. Use Tab para percorrer as UFs e Enter para selecionar. A seleção também está disponível na lista de estados.</desc>
        {geometry.map(g=>{
          const state=states.find(s=>s.uf===g.uf);
          return <path key={g.uf} d={g.path} fill={tariffColor(state.media,min,max)}
            fillRule="evenodd" role="button" tabIndex={0}
            aria-label={`${state.nome}: ${money(state.media)} por kWh. ${state.quantidade} ${state.quantidade===1?'distribuidora':'distribuidoras'}.`}
            aria-pressed={selected===g.uf}
            className={`state-path ${selected===g.uf ? 'is-selected' : ''}`}
            onMouseEnter={()=>setHovered(g.uf)} onMouseLeave={()=>setHovered(null)}
            onFocus={()=>setHovered(g.uf)} onBlur={()=>setHovered(null)}
            onClick={()=>onSelect(g.uf)} onKeyDown={e=>{
              if(e.key==='Enter'||e.key===' '){e.preventDefault();onSelect(g.uf);}
            }}><title>{state.nome} · {money(state.media)}/kWh</title></path>;
        })}
      </svg>
      {tooltip && <div className="map-tooltip pointer-events-none absolute left-0 top-3" aria-hidden="true">
        <span className="font-medium">{tooltip.nome}</span><span className="ml-3 tabular-nums text-secondary">{money(tooltip.media)}</span>
      </div>}
    </div>
    <div className="flex flex-wrap items-center justify-between gap-4 border-t border-line pt-4">
      <p className="text-xs text-secondary">Média simples · R$/kWh</p>
      <div aria-label={`Escala: ${money(min)} a ${money(max)} por kWh`}>
        <div className="mb-1.5 flex gap-0.5" aria-hidden="true">{palette.map(color=><span key={color} className="h-1.5 w-7" style={{backgroundColor:color}} />)}</div>
        <div className="flex justify-between text-[10px] tabular-nums text-secondary"><span>{decimal(min)}</span><span>{decimal(max)}</span></div>
      </div>
    </div>
    <p className="mt-3 text-[10px] text-subtle">Cinza: sem dados</p>
  </section>;
}
