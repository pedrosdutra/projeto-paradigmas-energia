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
