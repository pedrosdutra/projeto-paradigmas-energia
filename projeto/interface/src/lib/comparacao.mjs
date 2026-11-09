// O ranking já vem ordenado pelo Python, antes do arredondamento para a tela.
export function compararEstados(referencia, selecao) {
  const escolhidos = referencia.estados.filter(estado => selecao.includes(estado.uf));
  const porUf = new Map(escolhidos.map(estado => [estado.uf, estado]));
  const comTarifa = referencia.ranking
    .filter(uf => porUf.has(uf))
    .map(uf => porUf.get(uf));
  const semTarifa = escolhidos.filter(estado => estado.media == null);

  const maior = comTarifa[0];
  const menor = comTarifa.at(-1);
  return {
    linhas: [...comTarifa, ...semTarifa],
    maior: maior ? Number(maior.media) : null,
    diferenca: comTarifa.length >= 2 ? maior.diferencas[menor.uf] : null,
  };
}

export function alternarEstado(selecao, uf) {
  return selecao.includes(uf)
    ? selecao.filter(atual => atual !== uf)
    : [...selecao, uf];
}
