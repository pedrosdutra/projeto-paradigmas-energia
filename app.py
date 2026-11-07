"""Servidor local do painel React; os cálculos ficam no núcleo Python.

O HTML compilado contém os resultados exportados de fontes oficiais. Nenhum
cálculo tarifário ou escolha de fonte é realizado neste invólucro de interface.
"""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

PAINEL = Path(__file__).resolve().parent / 'frontend' / 'dist' / 'painel.html'

st.set_page_config(page_title='Energia em perspectiva', layout='wide')

if not PAINEL.is_file():
    st.error('A interface ainda não foi compilada. Siga a seção de desenvolvimento do README.')
    st.code('python exportar_frontend.py\ncd frontend\nnpm install\nnpm run build')
    st.stop()

# Uma única área de navegação: o iframe ocupa a janela e controla sua rolagem.
st.markdown('''<style>
    header[data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], #MainMenu, footer {display:none;}
    .block-container {padding:0!important; max-width:none!important;}
    [data-testid="stMainBlockContainer"] {padding:0!important;}
    [data-testid="stVerticalBlock"] {gap:0;}
    [data-testid="stMain"] {overflow:hidden;}
    iframe[title="streamlit.components.v1.html"], iframe[title="st.iframe"] {
        display:block; width:100%; height:100dvh; border:0;
    }
</style>''', unsafe_allow_html=True)

components.html(PAINEL.read_text(encoding='utf-8'), height=1000, scrolling=True)
