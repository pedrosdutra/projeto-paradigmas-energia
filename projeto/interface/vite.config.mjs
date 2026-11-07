import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  // O Streamlit abre o HTML diretamente, com as imagens pequenas incorporadas.
  build: { target: 'es2020', cssCodeSplit: false, assetsInlineLimit: 64 * 1024 },
});
