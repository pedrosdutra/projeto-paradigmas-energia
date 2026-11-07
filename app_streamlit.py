"""Interface: uma fonte oficial, referências disponíveis e consulta por estado."""
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
from arquivos import ler_csv, ler_json
from processamento import processar, normalizar_vinculos, UFS
from analise import fotografia, resumir, ranking
from visualizacao import criar_mapa

PASTA = Path(__file__).resolve().parent / 'dados'
ROTULO = 'ANEEL — recorte oficial; cálculo acadêmico'
NOMES = dict(zip(UFS, ('Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará',
    'Distrito Federal','Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul',
    'Minas Gerais','Pará','Paraíba','Paraná','Pernambuco','Piauí','Rio de Janeiro',
    'Rio Grande do Norte','Rio Grande do Sul','Rondônia','Roraima','Santa Catarina',
    'São Paulo','Sergipe','Tocantins')))

st.set_page_config(page_title='Energia em perspectiva', page_icon='⚡', layout='wide')
# Ajustes visuais locais; as cores de texto seguem o tema do Streamlit.
st.markdown('''<style>
    .block-container {padding-top: 4rem; padding-bottom: 2rem; max-width: 1440px;}
    h1 {letter-spacing: -.045em; padding-bottom: .25rem !important;}
    [data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22);
        border-radius: 14px; padding: 14px 18px; height: 100%;}
    [data-testid="stMetricValue"] {font-size: 1.85rem;}
    .fonte {display:inline-block; padding:6px 12px; border-radius:20px;
        color:#167a70; background:#e5f5ef; font-size:.8rem; font-weight:600;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
    .stTabs [data-baseweb="tab"] {font-weight:600;}
    @media (max-width: 700px) {.block-container {padding-top: 4rem;}}
</style>''', unsafe_allow_html=True)

@st.cache_data
def carregar_dados(tarifas_modificadas, vinculos_modificados):
    """Só os dois arquivos oficiais alimentam o painel; atualizações invalidam o cache."""
    return (processar(ler_csv(PASTA / 'tarifas_aneel.csv')),
            normalizar_vinculos(ler_csv(PASTA / 'mapeamento_aneel.csv')))

@st.cache_data
def referencias_disponiveis(tarifas, vinculos):
    """Oferece datas finais dos vínculos com ao menos uma tarifa compatível.

    Evita um calendário que permita selecionar meses sem evidência geográfica.
    A data continua explícita: nenhum desses resultados é uma média anual.
    """
    return tuple(sorted({v.fim for v in vinculos if any(
        t.cnpj == v.cnpj and t.inicio <= v.fim <= t.fim for t in tarifas)}))

def br(valor):
    return f'R$ {float(valor):.4f}'.replace('.', ',') if valor is not None else 'Sem dado'

st.markdown('<span class="fonte">● Fonte única de tarifas: ANEEL</span>', unsafe_allow_html=True)
st.title('Energia em perspectiva')
st.caption('Compare tarifas residenciais pelo Brasil e consulte as distribuidoras de cada estado.')

try:
    resultado, vinculos = carregar_dados((PASTA/'tarifas_aneel.csv').stat().st_mtime_ns,
                                         (PASTA/'mapeamento_aneel.csv').stat().st_mtime_ns)
except (OSError, ValueError) as erro:
    st.error('A base oficial não pôde ser carregada. Atualize os arquivos da ANEEL conforme o manual.')
    with st.expander('Detalhes do problema'):
        st.code(str(erro), language=None)
    st.stop()

datas = referencias_disponiveis(resultado.tarifas, vinculos)
if not datas:
    st.warning('A base oficial ainda não possui uma referência com tarifas e vínculos geográficos compatíveis.')
    st.stop()

filtro, contexto = st.columns([1, 3], vertical_alignment='bottom')
with filtro:
    anos = tuple(sorted({d.year for d in datas}))
    ano = st.selectbox('Ano de referência', anos, index=len(anos)-1, key='ano_referencia')
    datas_ano = tuple(d for d in datas if d.year == ano)
    # Uma única data dispensa outro controle; se houver mais, oferecemos as opções reais.
    referencia = (st.selectbox('Data disponível', datas_ano, index=len(datas_ano)-1,
                   format_func=lambda d:d.strftime('%d/%m/%Y'), key=f'referencia_{ano}')
                  if len(datas_ano) > 1 else datas_ano[0])
with contexto:
    st.write(f'**Tarifas vigentes em {referencia:%d/%m/%Y}** · Residencial comum · Convencional')
    st.caption('Apenas períodos com tarifas e mapeamento disponíveis. Valores em R$/kWh, calculados por TE + TUSD.')

foto = fotografia(resultado.tarifas, vinculos, referencia)
resumos = resumir(foto.itens)
ordem = ranking(resumos)
c1, c2, c3, c4 = st.columns(4)
c1.metric('UFs com dados', f'{len(ordem)} / 27')
c2.metric('Distribuidoras incluídas', len({i.tarifa.cnpj for i in foto.itens}))
c3.metric(f'Menor média · {ordem[-1].uf}' if ordem else 'Menor média', br(ordem[-1].media) if ordem else 'Sem dado')
c4.metric(f'Maior média · {ordem[0].uf}' if ordem else 'Maior média', br(ordem[0].media) if ordem else 'Sem dado')
st.caption('Média simples das distribuidoras observadas em cada UF. Não representa a conta final nem uma tarifa oficial estadual.')

explorar, classificar, metodologia = st.tabs(['Mapa e estados', 'Ranking completo', 'Sobre os dados'])
with explorar:
    mapa_col, detalhe_col = st.columns([1.4, 1], gap='large')
    with mapa_col:
        st.subheader('Explore o Brasil')
        st.caption('Clique em um estado para ver os detalhes ao lado. Cinza indica ausência de dados.')
        try:
            figura = criar_mapa(resumos, ler_json(PASTA/'brasil_ufs.geojson'))
            evento = st.plotly_chart(figura, key=f'mapa_aneel_{referencia}', on_select='rerun',
                selection_mode='points', width='stretch', theme=None,
                config={'displaylogo':False, 'scrollZoom':False})
            pontos = evento.selection.points
            if pontos:
                uf_clicada = pontos[-1].get('customdata', [None])[0]
                selecao = (referencia.isoformat(), uf_clicada)
                if uf_clicada in UFS and st.session_state.get('ultima_selecao_mapa') != selecao:
                    st.session_state['uf_detalhe'] = uf_clicada
                    st.session_state['ultima_selecao_mapa'] = selecao
            else:
                st.session_state.pop('ultima_selecao_mapa', None)
        except (OSError, ValueError, KeyError) as erro:
            st.warning('O mapa não está disponível. Use o seletor de estado ao lado.')
            with st.expander('Detalhes do mapa'):
                st.write(str(erro))

    with detalhe_col:
        st.subheader('Detalhes do estado')
        uf = st.selectbox('Estado ou Distrito Federal', UFS, key='uf_detalhe',
                           format_func=lambda sigla:f'{NOMES[sigla]} ({sigla})')
        resumo = next(r for r in resumos if r.uf == uf)
        detalhes = tuple(sorted(filter(lambda item:item.uf == uf, foto.itens), key=lambda i:i.tarifa.total))
        if detalhes:
            st.metric(f'Média em {NOMES[uf]}', br(resumo.media), help='TE + TUSD; média simples entre as distribuidoras observadas nesta UF.')
            st.caption(f'{resumo.quantidade} distribuidora(s) · De {br(resumo.minima)} a {br(resumo.maxima)} por kWh')
            st.dataframe(pd.DataFrame([{'Distribuidora':i.tarifa.agente,
                'TE':float(i.tarifa.te),'TUSD':float(i.tarifa.tusd),'Total':float(i.tarifa.total)} for i in detalhes]),
                hide_index=True, width='stretch', height=min(320, 38+35*len(detalhes)),
                column_config={c:st.column_config.NumberColumn(c, format='R$ %.4f') for c in ['TE','TUSD','Total']})
            st.caption('TE: Tarifa de Energia · TUSD: Tarifa de Uso do Sistema de Distribuição. Todos os valores em R$/kWh.')
            with st.expander('Ver vigências e resoluções'):
                st.dataframe(pd.DataFrame([{'Distribuidora':i.tarifa.agente,'CNPJ':i.tarifa.cnpj,
                    'Início':i.tarifa.inicio.strftime('%d/%m/%Y'),'Fim':i.tarifa.fim.strftime('%d/%m/%Y'),
                    'Resolução':i.tarifa.resolucao} for i in detalhes]),hide_index=True,width='stretch')
        else:
            st.info(f'Não há dado comparável para {NOMES[uf]} nesta referência.')

with classificar:
    st.subheader('Compare as médias por estado')
    st.caption(f'Referência: {referencia:%d/%m/%Y} · Ordenação da maior para a menor média. Empates seguem a sigla da UF.')
    registros = [{'Estado':NOMES[r.uf],'UF':r.uf,'Média (R$/kWh)':float(r.media),
        'Distribuidoras':r.quantidade,'Mínima':float(r.minima),'Máxima':float(r.maxima)} for r in ordem]
    tabela = pd.DataFrame(registros, columns=['Estado','UF','Média (R$/kWh)','Distribuidoras','Mínima','Máxima'])
    if not ordem:
        st.info('Não há dados comparáveis para montar o ranking nesta referência.')
    st.dataframe(tabela, hide_index=True, width='stretch', height=520,
        column_config={c:st.column_config.NumberColumn(format='R$ %.4f') for c in ['Média (R$/kWh)','Mínima','Máxima']})
    exportacao = tabela.assign(Referencia=referencia.isoformat(), Origem=ROTULO,
                               Metodo='Media simples entre distribuidoras observadas')
    st.download_button('Baixar ranking em CSV', exportacao.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),
        file_name=f'ranking_aneel_{referencia}.csv', mime='text/csv')

with metodologia:
    st.subheader('Dados oficiais, comparação transparente')
    st.write('As tarifas e as evidências de atendimento das distribuidoras vêm da ANEEL. O desenho dos estados vem do IBGE. A base é carregada automaticamente, sem troca de fonte ou envio de arquivos pela interface.')
    try:
        fontes = ler_json(PASTA/'fontes.json')
        coletado = datetime.fromisoformat(fontes['coletado_em_utc']).strftime('%d/%m/%Y')
        st.caption(f'Coleta incluída: {coletado} · Dados salvos localmente, sem consulta em tempo real.')
    except (OSError, ValueError, KeyError):
        fontes = None
        st.caption('Data de coleta indisponível no manifesto local.')
    st.markdown('''**Como calculamos**

1. Selecionamos tarifa de aplicação, B1, modalidade convencional, classe e subclasse residencial comum.
2. Validamos TE e TUSD e convertemos `R$/MWh` para `R$/kWh` dividindo por 1.000.
3. Escolhemos os registros vigentes na data exibida. Cada CNPJ conta uma vez por UF; conflitos são excluídos.
4. Relacionamos as distribuidoras às UFs com evidência municipal de atendimento válida no período.
5. Calculamos a média simples das distribuidoras observadas em cada UF.

**Como interpretar**

O resultado é uma fotografia da data, não uma média anual. Não há ponderação por consumo ou clientes, e a cobertura pode ser parcial. Não acrescentamos tributos, bandeiras ou iluminação pública; tratamentos já incorporados à fonte não são desfeitos. Os valores entre anos são nominais, sem ajuste pela inflação.''')
    st.markdown('[Tarifas de aplicação — ANEEL](https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica) · [Atendimento municipal — ANEEL](https://dadosabertos.aneel.gov.br/dataset/indger-indicadores-gerenciais-da-distribuicao)')
    with st.expander('Qualidade da base e registros excluídos'):
        st.write({'Linhas carregadas':resultado.total_linhas,'Fora do perfil':resultado.fora_recorte,
            'Linhas inválidas':len(resultado.problemas),'CNPJs com tarifas conflitantes':len(foto.conflitos),
            'CNPJs sem vínculo válido na data':len(foto.sem_mapeamento)})
        if resultado.problemas:
            st.dataframe([{'Linha':p.linha,'Motivo':p.motivo} for p in resultado.problemas], hide_index=True)
        if foto.conflitos:
            st.write('Conflitos excluídos:', foto.conflitos)
        if foto.sem_mapeamento:
            st.write('Sem mapeamento no período:', foto.sem_mapeamento)
    if fontes:
        with st.expander('Registro técnico da coleta'):
            st.json(fontes)

st.divider()
st.caption('Projeto acadêmico de Programação Funcional · Tarifas e atendimento: ANEEL · Malha geográfica: IBGE')
