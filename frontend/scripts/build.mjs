import { build } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { rankingCsv } from '../src/lib/format.mjs';

await build();
// Uma versão autocontida permite usar a interface dentro do Streamlit,
// sem CDN de JavaScript, outro servidor ou Node instalado na apresentação.
let html=await fs.readFile('dist/index.html','utf8');
for(const match of [...html.matchAll(/<script\b[^>]*src="([^"]+)"[^>]*><\/script>/g)]) {
  const js=await fs.readFile(path.join('dist',match[1]),'utf8');
  html=html.replace(match[0],()=>`<script type="module">${js.replace(/<\/script/gi,'<\\/script')}</script>`);
}
for(const match of [...html.matchAll(/<link\b[^>]*href="([^"]+\.css)"[^>]*>/g)]) {
  const css=await fs.readFile(path.join('dist',match[1]),'utf8');
  html=html.replace(match[0],()=>`<style>${css}</style>`);
}
// Identifica o snapshot para o teste detectar HTML compilado com dados antigos.
const snapshot = await fs.readFile('src/data/painel.json');
const checksum = createHash('sha256').update(snapshot).digest('hex');
html = html.replace('</head>', `<meta name="dados-sha256" content="${checksum}"></head>`);
await fs.writeFile('dist/painel.html',html);
// Cópias prontas para uso local, inclusive em navegadores que restringem downloads.
await fs.mkdir('dist/rankings', { recursive: true });
for (const reference of JSON.parse(snapshot).referencias) {
  await fs.writeFile(`dist/rankings/tarifas_aneel_${reference.data}.csv`, rankingCsv(reference));
}
// GitHub Pages publica esta pasta estática. Não executa o servidor Python.
await fs.mkdir('../docs', { recursive: true });
await fs.writeFile('../docs/index.html', html);
await fs.writeFile('../docs/.nojekyll', '');
console.log('Interface autocontida: dist/painel.html');
console.log('Protótipo para GitHub Pages: ../docs/index.html');
