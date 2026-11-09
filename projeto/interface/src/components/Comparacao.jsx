import { money } from '../lib/format.mjs';
import { alternarEstado } from '../lib/comparacao.mjs';

export default function Comparacao({ estados, selecao, setSelecao, resultado }) {
  return <section aria-labelledby="titulo-comparacao">
    <h2 id="titulo-comparacao" className="text-xl font-medium tracking-tight">Comparar estados</h2>
    <fieldset className="mt-5 border-b border-line pb-6">
      <legend className="text-xs text-secondary">Escolha duas ou mais UFs</legend>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {estados.map(({ uf, nome }) => (
          <button key={uf} type="button" className="uf-toggle" title={nome}
            aria-label={`${nome} (${uf})`} aria-pressed={selecao.includes(uf)}
            onClick={() => setSelecao(anterior => alternarEstado(anterior, uf))}>
            {uf}
          </button>
        ))}
      </div>
    </fieldset>

    <div className="mt-6 flex flex-wrap items-baseline justify-between gap-3">
      <div>
        <h3 className="font-medium">Tarifa média por kWh</h3>
        <p className="mt-1 text-xs text-subtle">TE + TUSD · Média das distribuidoras observadas</p>
      </div>
      {resultado.diferenca !== null && <p className="text-sm text-secondary">
        Diferença entre maior e menor <strong className="ml-1 font-medium tabular-nums text-accent">{money(resultado.diferenca)}/kWh</strong>
      </p>}
    </div>
    {resultado.linhas.length > 0 && <ul className="mt-4" aria-label="Tarifas dos estados selecionados">
      {resultado.linhas.map(estado => (
        <li key={estado.uf} className="border-b border-line py-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
            <span className="font-medium">{estado.nome} <span className="ml-1 text-xs text-subtle">{estado.uf}</span></span>
            <span className="tabular-nums">{money(estado.media)}{estado.media != null && ' / kWh'}</span>
          </div>
          {estado.media != null && <>
            <div aria-hidden="true" className="my-2 h-1.5 bg-muted">
              <div className="h-full bg-accent" style={{width: `${resultado.maior > 0 ? Number(estado.media) / resultado.maior * 100 : 0}%`}} />
            </div>
            <p className="text-xs text-subtle">{estado.quantidade} {estado.quantidade === 1 ? 'distribuidora' : 'distribuidoras'}</p>
          </>}
        </li>
      ))}
    </ul>}
    {resultado.diferenca === null && <p className="mt-5 text-sm text-secondary" role="status">
      {selecao.length < 2 ? 'Selecione pelo menos dois estados para comparar.' : 'A diferença exige dois estados com tarifa nessa data.'}
    </p>}
  </section>;
}
