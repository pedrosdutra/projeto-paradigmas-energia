import { build } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

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
// A página guarda a identificação dos dados usados nesta edição.
const dados = await fs.readFile('src/data/painel.json');
const codigo = createHash('sha256').update(dados).digest('hex');
html = html.replace('</head>', `<meta name="dados-sha256" content="${codigo}"></head>`);

const pastaPublicada = new URL('../../../docs/', import.meta.url);
await fs.mkdir(pastaPublicada, { recursive: true });
await fs.writeFile(new URL('index.html', pastaPublicada), html);
await fs.writeFile(new URL('.nojekyll', pastaPublicada), '');
console.log('Painel pronto em docs/index.html');
