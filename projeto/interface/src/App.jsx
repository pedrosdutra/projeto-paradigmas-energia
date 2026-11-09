import { useEffect, useState } from 'react';
import data from './data/painel.json';
// Marca publicada no Portal de Dados Abertos: https://dadosabertos.aneel.gov.br/logo-aneel.png
import marcaAneel from './assets/aneel.png';
import MapView from './components/MapView';
import StateDetail from './components/StateDetail';
import Ranking from './components/Ranking';
import Comparacao from './components/Comparacao';
import { compararEstados } from './lib/comparacao.mjs';
import SearchDialog from './components/SearchDialog';
import { money, dateLabel, downloadRanking } from './lib/format.mjs';

function SearchIcon(){return <svg width="15" height="15" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" strokeWidth="1.4"/><path d="m13 13 4 4" stroke="currentColor" strokeWidth="1.4"/></svg>;}
function DownloadIcon(){return <svg width="15" height="15" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 2v10m-4-4 4 4 4-4M3 13v4h14v-4" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>;}

const navigation=[['overview','Visão geral'],['ranking','Ranking'],['comparacao','Comparar estados']];

export default function App(){
  const [page,setPage]=useState('overview');
  const [referenceId,setReferenceId]=useState(data.referencias.at(-1)?.data);
  const [uf,setUf]=useState('CE');
  const [selecao,setSelecao]=useState(['CE','BA']);
  const [searchOpen,setSearchOpen]=useState(false);
  const [notice,setNotice]=useState('');
  const reference=data.referencias.find(r=>r.data===referenceId);
  useEffect(()=>{
    const handleKey=e=>{
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){
        e.preventDefault();setSearchOpen(v=>!v);
      }
    };
    window.addEventListener('keydown',handleKey);
    return ()=>window.removeEventListener('keydown',handleKey);
  },[]);
  useEffect(()=>{if(notice){const timer=setTimeout(()=>setNotice(''),4000);return()=>clearTimeout(timer);}},[notice]);
  if(!reference) return <main className="mx-auto max-w-xl px-6 py-20"><h1 className="text-2xl font-medium">Base oficial indisponível</h1><p className="mt-4 text-secondary">Gere novamente os resultados a partir dos arquivos oficiais da ANEEL.</p></main>;
  const state=reference.estados.find(s=>s.uf===uf);
  const ordered=reference.ranking.map(code=>reference.estados.find(s=>s.uf===code));
  const lowest=ordered.at(-1),highest=ordered[0];
  const selectState=code=>{setUf(code);setPage('overview');};
  const comparacao = page === 'comparacao' ? compararEstados(reference, selecao) : null;
  const exportCsv = () => {
    downloadRanking(reference, comparacao?.linhas);
    setNotice(comparacao ? 'Comparação preparada para download.' : 'Ranking preparado para download.');
  };

  return <div className="app-shell">
    <a href="#main" className="skip-link">Ir para o conteúdo</a>
    <aside className="sidebar">
      <a href="#main" onClick={()=>setPage('overview')} className="inline-flex w-fit items-center" aria-label="ANEEL, voltar à visão geral do projeto">
        <img className="brand-logo" src={marcaAneel} alt="ANEEL" width="120" height="32" />
      </a>
      <p className="mb-3 mt-12 px-2 text-[10px] font-medium uppercase tracking-[.14em] text-subtle">Área de análise</p>
      <nav aria-label="Navegação principal" className="flex gap-1 lg:flex-col">{navigation.map(([id,label])=><button key={id} onClick={()=>setPage(id)} aria-current={page===id?'page':undefined} className={`nav-item ${page===id?'active':''}`}>{label}</button>)}</nav>
      <div className="sidebar-footer"><p className="text-[11px] font-medium text-body">Projeto Paradigmas</p><span className="mt-2 block text-[10px] tabular-nums text-subtle">Brasil · 26 estados + DF</span></div>
    </aside>

    <div className="min-w-0">
      <header className="topbar">
        <div className="text-xs text-subtle">Energia <span className="mx-3 text-subtle">/</span><span className="text-body">{navigation.find(([id])=>id===page)[1]}</span></div>
        <button className="search-button" onClick={()=>setSearchOpen(true)} aria-label="Buscar estado. Atalho Control K ou Command K."><SearchIcon/><span>Buscar estado</span><kbd className="ml-4 hidden sm:inline">Ctrl K</kbd></button>
      </header>
      <main id="main" tabIndex={-1} className="main-content">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div><p className="eyebrow">Tarifas residenciais · Brasil</p><h1 className="mt-3 text-[30px] font-medium leading-[1.15] tracking-[-.045em] sm:text-[36px]">Energia, em perspectiva.</h1></div>
          <div className="mt-1 flex items-center gap-3"><span className="source-badge"><span className="h-1.5 w-1.5 rounded-full bg-accent"/>Fonte única: ANEEL</span></div>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-b border-line pb-5">
          <div className="flex flex-wrap items-center gap-3 text-xs"><label htmlFor="reference" className="text-secondary">Referência</label>
            <select id="reference" value={referenceId} onChange={e=>setReferenceId(e.target.value)} className="select-control text-xs">
              {data.referencias.map(r=><option key={r.data} value={r.data}>{dateLabel(r.data)}</option>)}
            </select><span className="hidden h-3 border-l border-line sm:inline"/><span className="text-subtle">B1 · Residencial comum · Convencional</span>
          </div>
          <button className="button-secondary disabled:opacity-50" onClick={exportCsv} disabled={comparacao?.linhas.length === 0}><DownloadIcon/>Exportar CSV</button>
        </div>
        {page==='overview' && <>
          <dl className="summary-strip">
            <div><dt>Cobertura da análise</dt><dd>{reference.cobertura}<span className="ml-1 text-lg font-normal text-subtle">/ 27 UFs</span></dd><p>{reference.distribuidoras} distribuidoras observadas</p></div>
            <div><dt>Menor média observada</dt><dd>{money(lowest?.media)}</dd><p>{lowest?.nome??'Sem dado'}</p></div>
            <div><dt>Maior média observada</dt><dd>{money(highest?.media)}</dd><p>{highest?.nome??'Sem dado'}</p></div>
          </dl>
          <div className="grid gap-9 border-t border-line pt-7 lg:grid-cols-[minmax(0,1.6fr)_minmax(300px,1fr)] lg:gap-0">
            <MapView states={reference.estados} geometry={data.mapa} selected={uf} onSelect={setUf}/>
            <StateDetail key={`${referenceId}-${uf}`} state={state} states={reference.estados} onSelect={setUf} date={reference.data} rank={reference.ranking.indexOf(uf)+1}/>
          </div>
        </>}
        <div className={page==='overview'?'hidden':'pt-9'}>
          {page==='ranking' && <Ranking reference={reference} onSelect={selectState}/>}
          {comparacao && <Comparacao estados={reference.estados} selecao={selecao} setSelecao={setSelecao} resultado={comparacao}/>}
        </div>
      </main>
    </div>
    <SearchDialog open={searchOpen} onClose={()=>setSearchOpen(false)} states={reference.estados} onSelect={selectState}/>
    {notice && <div role="status" className="notice">{notice}</div>}
  </div>;
}
