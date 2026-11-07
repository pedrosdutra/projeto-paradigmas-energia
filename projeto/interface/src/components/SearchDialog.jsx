import { useEffect, useRef, useState } from 'react';
import { searchStates } from '../lib/format.mjs';

export default function SearchDialog({ open, onClose, states, onSelect }) {
  const dialog=useRef(null), input=useRef(null);
  const [query,setQuery]=useState('');
  useEffect(()=>{
    if(open){setQuery('');dialog.current.showModal();input.current.focus();}
    else if(dialog.current.open) dialog.current.close();
  },[open]);
  return <dialog ref={dialog} className="search-dialog" aria-labelledby="search-heading"
    onCancel={onClose} onClose={onClose} onClick={e=>{if(e.target===dialog.current)onClose();}}>
    <div className="flex items-center justify-between border-b border-line px-5 py-4">
      <h2 id="search-heading" className="text-sm font-medium">Buscar estado</h2>
      <button onClick={onClose} className="rounded border border-line px-2 py-1 text-[10px] text-secondary" aria-label="Fechar busca">Esc</button>
    </div>
    <label className="sr-only" htmlFor="state-search">Nome ou sigla do estado</label>
    <input ref={input} id="state-search" type="search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Digite um nome ou uma sigla…" className="w-full border-b border-line bg-transparent px-5 py-4 text-sm outline-none" />
    <div className="max-h-80 overflow-y-auto p-2">
      {searchStates(states,query).map(s=><button key={s.uf} onClick={()=>{onSelect(s.uf);onClose();}}
        className="flex w-full items-center justify-between rounded px-3 py-3 text-left text-sm hover:bg-muted"><span>{s.nome}</span><span className="text-xs text-subtle">{s.uf}</span></button>)}
      {!searchStates(states,query).length && <p className="p-5 text-sm text-secondary" role="status">Nenhum estado encontrado.</p>}
    </div>
  </dialog>;
}
