import { build } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

await build();
// Uma versão autocontida permite usar a interface dentro do Streamlit,
// sem CDN de JavaScript, outro servidor ou Node instalado na apresentação.
const pagina = await fs.readFile('dist/index.html','utf8');
const incorporar = async (pagina, padrao, renderizar) => {
  const trechos = await Promise.all(Array.from(pagina.matchAll(padrao), async ([tag, arquivo]) => {
    const conteudo = await fs.readFile(path.join('dist', arquivo), 'utf8');
    return [tag, renderizar(conteudo)];
  }));
  return trechos.reduce((html, [tag, conteudo]) => html.replace(tag, () => conteudo), pagina);
};
const comScripts = await incorporar(pagina, /<script\b[^>]*src="([^"]+)"[^>]*><\/script>/g,
  js => `<script type="module">${js.replace(/<\/script/gi,'<\\/script')}</script>`);
let html = await incorporar(comScripts, /<link\b[^>]*href="([^"]+\.css)"[^>]*>/g,
  css => `<style>${css}</style>`);
const dados = await fs.readFile('src/data/painel.json');
const codigo = createHash('sha256').update(dados).digest('hex');
html = html.replace('</head>', `<meta name="dados-sha256" content="${codigo}"></head>`);

const pastaPublicada = new URL('../../../docs/', import.meta.url);
await fs.mkdir(pastaPublicada, { recursive: true });
await fs.writeFile(new URL('index.html', pastaPublicada), html);
await fs.writeFile(new URL('.nojekyll', pastaPublicada), '');
