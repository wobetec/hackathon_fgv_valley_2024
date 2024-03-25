from dash import Dash, dcc, html, Input, Output, callback, State
import datetime
import dash
import plotly.express as px
from api.dados import Datalake, MAP_BOUNDS
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(
    __name__,
    path='/pluviometria',
    title='Pluviometria',
    name='Pluviometria',
    order=2
)

pluviometros = pd.DataFrame([
    {'Origem': 'AlertaRio', "TabelaTaxas": 'rj-cor.clima_pluviometro.taxa_precipitacao_alertario_5min', 'TabelaEstacoes': 'rj-cor.clima_pluviometro.estacoes_alertario'},
    {'Origem': 'Cemaden', "TabelaTaxas": 'rj-cor.clima_pluviometro.taxa_precipitacao_cemaden', 'TabelaEstacoes': 'rj-cor.clima_pluviometro.estacoes_cemaden'},
    {'Origem': 'INEA', "TabelaTaxas": 'rj-cor.clima_pluviometro.taxa_precipitacao_inea', 'TabelaEstacoes': 'rj-cor.clima_pluviometro.estacoes_inea'},
    {'Origem': 'Websirene', "TabelaTaxas": 'rj-cor.clima_pluviometro.taxa_precipitacao_websirene', 'TabelaEstacoes': 'rj-cor.clima_pluviometro.estacoes_websirene'},
])

filtro = html.Div(
    id='pluviometria-filtro',
    className='filtro',
    children=[
        html.Div(
            className='input-group',
            children=[
                html.Label('Dados:'),
                dcc.Dropdown(
                    options=[
                        {'label': x.Origem, 'value': x.Origem}
                        for _, x in pluviometros.iterrows()
                    ],
                    value='AlertaRio',
                    id='pluviometria-filtro-origem',
                    clearable=False
                ),
            ]
        ),
        html.Div(
            className='input-group',
            children=[
                html.Label('Acumulado:'),
                dcc.Dropdown(
                    options=[15, 30, 45, 60, 90, 120, 240, 360, 720],
                    value=15,
                    id='pluviometria-filtro-acumulado',
                    clearable=False
                ),
                html.Label('min'),
            ]
        ),
        html.Div(
            className='input-group',
            children=[
                html.Label('Estação:'),
                dcc.Dropdown(
                    options=[15, 30, 45, 60, 90, 120, 240, 360, 720],
                    value=15,
                    id='pluviometria-filtro-estacao',
                    clearable=False
                ),
            ]
        ),
        html.Div(
            className='input-group',
            children=[
                html.Label('Data:'),
                dcc.DatePickerRange(
                    id='pluviometria-filtro-data',
                    min_date_allowed=datetime.date(1995, 8, 5),
                    max_date_allowed=datetime.date(2017, 9, 19),
                    initial_visible_month=datetime.date(2017, 8, 5),
                    end_date=datetime.date(2017, 8, 25)
                ),
            ]
        ),
        html.Div(
            [
                html.Button(
                    [
                        html.Img(src='./assets/images/download.svg', id='down-icon'),
                        'Taxas'
                    ],
                    id="pluviometria-download-taxas-button",
                    className='button-download'
                ),
                dcc.Download(id="pluviometria-download-taxas"),
            ],
            className='download-button'
        ),
        html.Div(
            [
                html.Button(
                    [
                        html.Img(src='./assets/images/download.svg', id='down-icon'),
                        'Estações'
                    ],
                    id="pluviometria-download-estacoes-button",
                    className='button-download'
                ),
                dcc.Download(id="pluviometria-download-estacoes"),
            ],
            className='download-button'
        ),
    ]
)

container = html.Div(
    id='pluviometria-container',
    children=[
        dcc.Graph(
            id='pluviometria-main-graph',
            style={
                'gridRowStart':1,
                'gridRowEnd': 2,
            },
        ),
        dcc.Graph(
            id='pluviometria-main-map',
            style={
                'gridRowStart':2,
                'gridRowEnd': 3,
            },
        ),
    ]
)

layout = html.Div(
    className='page',
    id='pluviometria',
    children=[
        filtro,
        container
    ]
)


@callback(
    Output("pluviometria-download-estacoes", "data"),
    Input("pluviometria-download-estacoes-button", "n_clicks"),
    State('pluviometria-filtro-origem', 'value'),
    prevent_initial_call=True,
    background=True,
)
def baixar_estacoes(n_clicks, origem):
    estacoes = Datalake.get(pluviometros[pluviometros.Origem == origem]['TabelaEstacoes'].iloc[0])
    return dcc.send_data_frame(estacoes.to_csv, "estacoes.csv")


@callback(
    Output("pluviometria-download-taxas", "data"),
    Input("pluviometria-download-taxas-button", "n_clicks"),
    State('pluviometria-filtro-origem', 'value'),
    prevent_initial_call=True,
    background=True,
)
def baixar_taxas(n_clicks, origem):
    taxas = Datalake.get(pluviometros[pluviometros.Origem == origem]['TabelaTaxas'].iloc[0])
    return dcc.send_data_frame(taxas.to_csv, "taxas.csv")


@callback(
    Output('pluviometria-main-graph', 'figure'),
    inputs=[
        Input('pluviometria-filtro-origem', 'value'),
        Input('pluviometria-filtro-acumulado', 'value'),
    ],
    background=True,
)
def update_pluviometria_main_chart(origem, acumulado):
    taxas = Datalake.get(pluviometros[pluviometros.Origem == origem]['TabelaTaxas'].iloc[0])
    estacoes = Datalake.get(pluviometros[pluviometros.Origem == origem]['TabelaEstacoes'].iloc[0])

    df = pd.melt(
        taxas, 
        id_vars=['id_estacao', 'data_medicao'],
        value_vars=[f'acumulado_chuva_{acumulado}min',],
        var_name='tempo',
        value_name='taxa',
    )
    df['data_medicao'] = pd.to_datetime(df['data_medicao'])
    df = df.dropna()
    df = df.sort_values('data_medicao')

    fig_graph = px.line(
        df[df.id_estacao == 1],
        x='data_medicao',
        y='taxa'
    )

    fig_map = px.scatter_mapbox(estacoes, lat="latitude", lon='longitude', hover_name='id_estacao', zoom=5)

    fig_graph.update_layout(transition_duration=300)
    fig_map.update_layout(
        transition_duration=300,
        mapbox_bounds=MAP_BOUNDS,
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig_graph

@callback(
    Output('pluviometria-main-map', 'figure'),
    inputs=[
        Input('pluviometria-filtro-origem', 'value')
    ],
    background=True,
)
def update_pluviometria_main_map(origem):
    estacoes = Datalake.get(pluviometros[pluviometros.Origem == origem]['TabelaEstacoes'].iloc[0])

    fig_map = px.scatter_mapbox(estacoes, lat="latitude", lon='longitude', hover_name='id_estacao', zoom=5)
    fig_map.update_layout(
        transition_duration=300,
        mapbox_bounds=MAP_BOUNDS,
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig_map
