from pathlib import Path

# Regressão da interface original, mantida como alternativa didática.
# O React é verificado por testes JS, integração do exportador e navegador.
import pytest

pytestmark = pytest.mark.legacy_ui
APP=Path(__file__).resolve().parents[1]/'app_streamlit.py'

def test_app_real_filtros_e_detalhe():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not app.exception
    assert app.metric[0].value=='27 / 27'
    app.selectbox(key='ano_referencia').select(2024).run()
    assert not app.exception and app.metric[0].value=='27 / 27'
    app.selectbox(key='uf_detalhe').select('DF').run()
    assert not app.exception
    assert 'Neoenergia Brasília' in app.dataframe[0].value['Distribuidora'].tolist()

def test_app_fonte_unica_e_referencias_validas():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not app.exception
    assert not app.radio and not app.get('file_uploader') and not app.date_input
    assert app.selectbox(key='ano_referencia').options==['2024','2025']
    assert [t.label for t in app.tabs]==['Mapa e estados','Ranking completo','Sobre os dados']
    assert any('31/12/2025' in m.value for m in app.markdown)
