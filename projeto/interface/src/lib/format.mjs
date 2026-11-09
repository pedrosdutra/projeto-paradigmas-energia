export const money = value => value == null ? 'Sem dado' : new Intl.NumberFormat('pt-BR', {
  style: 'currency', currency: 'BRL', minimumFractionDigits: 4, maximumFractionDigits: 4,
}).format(Number(value));
export const decimal = value => value == null ? '—' : new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 4, maximumFractionDigits: 4,
}).format(Number(value));
export const dateLabel = value => new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC',
}).format(new Date(value.slice(0,10) + 'T12:00:00Z'));
export const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export const searchStates = (states, query) => states.filter(s =>
  normalize(`${s.nome} ${s.uf}`).includes(normalize(query.trim())));
// Azul claro representa menor média; azul profundo representa maior média.
export const palette = ['#d6e9f7', '#a6c8e4', '#6fa7cf', '#367fb4', '#174c7a'];
export const noDataColor = '#454b55';
export function tariffColor(value, min, max) {
  if (value == null) return noDataColor;
  const position = max === min ? .5 : (Number(value) - min) / (max - min);
  return palette[Math.max(0, Math.min(4, Math.floor(position * 5)))];
}
// Exportamos os resultados vindos do Python, sem recalcular médias em JavaScript.
export function rankingCsv(reference, rows = reference.ranking.map(uf => reference.estados.find(s => s.uf === uf))) {
  const quote = v => `"${String(v).replaceAll('"','""')}"`;
  return '\ufeff' + [
    ['UF','Estado','Media_R$_kWh','Distribuidoras','Data','Fonte','Metodo'],
    ...rows.map(s => [s.uf,s.nome,s.media?.replace('.',',') ?? '',s.quantidade,reference.data,'ANEEL',
      'Media simples das distribuidoras observadas']),
  ].map(row => row.map(quote).join(';')).join('\r\n');
}
export function downloadRanking(reference, selecionados) {
  const url = URL.createObjectURL(new Blob([rankingCsv(reference, selecionados)], { type:'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href=url; link.download=`${selecionados ? 'comparativo_aneel' : 'tarifas_aneel'}_${reference.data}.csv`;
  document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url),1000);
}
