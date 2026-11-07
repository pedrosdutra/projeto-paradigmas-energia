import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { searchStates, rankingCsv, tariffColor, palette, noDataColor } from '../src/lib/format.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../src/data/painel.json',import.meta.url),'utf8'));

test('referências oficiais e geometria têm 27 UFs únicas',()=>{
  assert.equal(data.fonte,'ANEEL');
  assert.equal(new Set(data.mapa.map(x=>x.uf)).size,27);
  for(const r of data.referencias){
    assert.equal(new Set(r.estados.map(x=>x.uf)).size,27);
    assert.equal(r.ranking.length,r.cobertura);
    assert.ok(data.mapa.every(g=>/^M[\d.,LZM-]+$/.test(g.path)));
  }
});
test('busca encontra nome com ou sem acento e sigla',()=>{
  const states=data.referencias[0].estados;
  assert.deepEqual(searchStates(states,'ceara').map(s=>s.uf),['CE']);
  assert.deepEqual(searchStates(states,' DF ').map(s=>s.uf),['DF']);
  assert.equal(searchStates(states,'inexistente').length,0);
});
test('exportação mantém data, fonte e valores produzidos pelo Python',()=>{
  const r=data.referencias.at(-1),csv=rankingCsv(r);
  assert.ok(csv.includes('"ANEEL"'));
  assert.ok(csv.includes(r.data));
  const first=r.estados.find(s=>s.uf===r.ranking[0]);
  assert.ok(csv.split('\r\n')[1].includes(first.media.replace('.',',')));
  assert.equal(csv.split('\r\n').length,r.ranking.length+1);
});
test('ausência é distinta de zero e escala trata valores iguais',()=>{
  assert.equal(tariffColor(null,0,1),noDataColor);
  assert.notEqual(tariffColor(0,0,1),noDataColor);
  assert.equal(tariffColor(.5,.5,.5),palette[2]);
});
