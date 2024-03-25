from dash import Dash, dcc, html, Input, Output, callback, State
import datetime
import dash
import plotly.express as px
from api.dados import Datalake, MAP_BOUNDS
import dash_bootstrap_components as dbc
import pandas as pd
import json

dash.register_page(
    __name__,
    path='/cor_1746',
    title='COR x 1746',
    name='COR x 1746',
    order=4
)

df_1746 = Datalake.get('datario.adm_central_atendimento_1746.chamado')
df_cor = Datalake.get('rj-cor.adm_cor_comando.ocorrencias')

df_cor = df_cor[df_cor['data_inicio'] >= df_1746.data_inicio.min()]
df_cor = df_cor.sort_values(by='data_inicio')
df_1746 = df_1746.sort_values(by='data_inicio')
df_1746["data_inicio"] = pd.to_datetime(df_1746["data_inicio"]).dt.date
ocorrencias_1746 = df_1746.groupby("data_inicio").size().reset_index(name="contagem_1746")

df_cor["data_inicio"] = pd.to_datetime(df_cor["data_inicio"]).dt.date
ocorrencias_cor = df_cor.groupby("data_inicio").size().reset_index(name="contagem_cor")

ocorrencias_combinadas = pd.merge(ocorrencias_cor, ocorrencias_1746, how="inner", on="data_inicio")

ocorrencias_combinadas.rename(columns={"contagem_cor": "Contagem df_cor", "contagem_1746": "Contagem df_1746"}, inplace=True)

fig_graph = px.scatter(
    ocorrencias_combinadas,
    x="Contagem df_cor",
    y="Contagem df_1746",
    title="Comparação de 1746 e COR",
    labels={
        "Contagem df_cor": "Número de Chamadas COR",
        "Contagem df_1746": "Número de Chamadas 1746"
    },
    trendline="ols",
    trendline_color_override="red"
)

temp_1746 = df_1746[['latitude', 'longitude']].copy()
temp_1746['Tipo'] = '1746'
temp_cor = df_cor[['latitude', 'longitude']].copy()
temp_cor['Tipo'] = 'COR'
df = pd.concat([
    temp_1746,
    temp_cor
], ignore_index=True)

fig_map = px.scatter_mapbox(
    df,
    lat="latitude",
    lon='longitude',
    color='Tipo',
    zoom=5
)
fig_map.update_layout(
    transition_duration=300,
    mapbox_bounds=MAP_BOUNDS,
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0}
)

container = html.Div(
    id='cor_1746-container',
    children=[
        dcc.Graph(
            figure=fig_map,
            id='cor_1746-main-map',
            style={
                'gridColumnStart':2,
                'gridColumnEnd': 3,
            },
        ),
        dcc.Graph(
            figure=fig_graph,
            id='cor_1746-main-graph',
            style={
                'gridColumnStart':1,
                'gridColumnEnd': 2,
            },
        ),
    ]
)

layout = html.Div(
    className='page',
    children=[
        container,
    ]
)

