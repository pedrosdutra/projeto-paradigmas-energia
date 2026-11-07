"""Transforma resultados em figura Plotly; não consulta a internet."""
import plotly.graph_objects as go
from processamento import CODIGOS_UF

def criar_mapa(resumos, geojson):
    codigos={uf:codigo for codigo,uf in CODIGOS_UF}
    figura=go.Figure()
    # Fundo cinza mantém todas as 27 UFs, inclusive quando faltam tarifas.
    figura.add_trace(go.Choroplethmap(
        geojson=geojson,featureidkey='properties.codarea',
        locations=[codigos[r.uf] for r in resumos],z=[0]*len(resumos),
        customdata=[[r.uf] for r in resumos],text=[r.uf for r in resumos],
        colorscale=[[0,'#dbe3e9'],[1,'#dbe3e9']],showscale=False,
        marker_line_color='white',marker_line_width=1,
        hovertemplate='%{text}<br>Sem dado comparável<extra></extra>',name='Sem dados'))
    presentes=tuple(r for r in resumos if r.media is not None)
    if presentes:
        figura.add_trace(go.Choroplethmap(
            geojson=geojson,featureidkey='properties.codarea',
            locations=[codigos[r.uf] for r in presentes],z=[float(r.media) for r in presentes],
            customdata=[[r.uf,r.quantidade] for r in presentes],
            colorscale=[[0,'#d8efee'],[0.5,'#389c9a'],[1,'#124c68']],
            colorbar=dict(title='R$/kWh',thickness=12,len=0.65,tickfont=dict(color='#304450'),title_font=dict(color='#304450')),
            marker_line_color='white',marker_line_width=1,
            hovertemplate='<b>%{customdata[0]}</b><br>Média: R$ %{z:.4f}/kWh<br>%{customdata[1]} distribuidora(s)<extra></extra>',
            name='Tarifa média'))
    # white-bg dispensa mapas de terceiros, tokens e arquivos TopoJSON remotos.
    figura.update_layout(map=dict(style='white-bg',center=dict(lat=-14.2,lon=-53),zoom=2.9),
                          height=510,margin=dict(l=0,r=0,t=0,b=0),clickmode='event+select',
                          paper_bgcolor='white',uirevision='brasil',
                          font=dict(family='Arial, sans-serif',color='#304450'))
    return figura
