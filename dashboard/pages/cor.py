from dash import Dash, dcc, html, Input, Output, callback, State
import datetime
import dash
import plotly.express as px
from api.dados import Datalake, MAP_BOUNDS
import dash_bootstrap_components as dbc
import pandas as pd
from dateutil.relativedelta import relativedelta

dash.register_page(
    __name__,
    path='/cor',
    title='COR',
    name='COR',
    order=3
)

tabs = dbc.CardHeader(
    dbc.Tabs(
        [
            dbc.Tab(label="Ranking dos Bairros por Gravidade", tab_id="ranking"),
            dbc.Tab(label="Distribuição de Gravidade", tab_id="map"),
        ],
        id="cor-tabs",
        active_tab="ranking",
    )
)

container = html.Div(
    id='cor-container',
    children=[
        dcc.Graph(
            id='cor-main-graph',
        )
    ]
)

layout = html.Div(
    className='page',
    id='cor',
    children=[
        tabs,
        container
    ]
)

@callback(
    Output('cor-main-graph', 'figure'),
    Input("cor-tabs", "active_tab",)
)
def update_cor_main_chart(active_tab):
    df = Datalake.get('rj-cor.adm_cor_comando.ocorrencias')

    if active_tab == 'ranking':
        df_count = df.groupby(['bairro', 'gravidade'])['data_particao'].count().to_frame().rename(columns={'data_particao': 'count'}).reset_index()
        df_count = df_count[df_count.bairro.isin(df.bairro.value_counts()[:20].index)].sort_values('count')
        fig = px.bar(
            df_count, 
            y='bairro',
            x='count',
            color='gravidade',
            barmode='group',
            title='Top 20 Bairros com mais COR'
        )
    elif active_tab == 'map':
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon='longitude',
            color='gravidade',
            hover_name='tipo',
            zoom=5
        )
        fig.update_layout(
            transition_duration=300,
            mapbox_bounds=MAP_BOUNDS,
            mapbox_style="open-street-map",
            margin={"r":0,"t":0,"l":0,"b":0}
        )

    return fig