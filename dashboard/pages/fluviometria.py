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
    path='/fluviometria',
    title='Fluviometria',
    name='Fluviometria',
    order=5 
)


filtro = html.Div(
    id='fluviometria-filtro',
    className='filtro',
    children=[
        html.Div(
            className='input-group',
            children=[
                html.Label('Data:'),
                dcc.DatePickerRange(
                    id='fluviometria-filtro-data',
                    min_date_allowed=datetime.date(1995, 8, 5),
                    max_date_allowed=datetime.date(2100, 9, 19),
                    initial_visible_month=datetime.datetime.today().replace(hour=23, minute=59, second=59),
                    end_date=datetime.datetime.today().replace(hour=23, minute=59, second=59)
                ),
            ]
        ),
        html.Div(
            [
                html.Button(
                    [
                        html.Img(src='./assets/images/download.svg', id='down-icon'),
                        'Série'
                    ],
                    id="fluviometria-download-serie-button",
                    className='button-download'
                ),
                dcc.Download(id="fluviometria-download-serie"),
            ],
            className='download-button'
        ),
    ]
)


tabs = dbc.CardHeader(
    dbc.Tabs(
        [
            dbc.Tab(label="Qualidade da Lagoa", tab_id="lagoa"),
            dbc.Tab(label="Bacia do Mangue", tab_id="mangue"),
        ],
        id="fluviometria-tabs",
        active_tab="lagoa",
    )
)

container = html.Div(
    id='fluviometria-container',
    children=[
        dcc.Graph(
            id='fluviometrai-main-graph',
        )
    ]
)

layout = html.Div(
    className='page',
    id='fluviometria',
    children=[
        filtro,
        tabs,
        container
    ]
)

@callback(
    Output("fluviometria-download-serie", "data"),
    Input("pluviometria-download-taxas-button", "n_clicks"),
    State("fluviometria-tabs", "active_tab",),
    prevent_initial_call=True
)
def baixar_serie_fluviometria(n_clicks, active_tab):
    if active_tab == 'mangue':
        df = Datalake.get('rj-rioaguas.saneamento_drenagem.nivel_reservatorio')
    elif active_tab == 'lagoa':
        df = Datalake.get('rj-rioaguas.saneamento_drenagem.qualidade_agua')
    return dcc.send_data_frame(df.to_csv, "serie.csv")

@callback(
    Output('fluviometrai-main-graph', 'figure'),
    Input('fluviometria-filtro-data', 'start_date'),
    Input('fluviometria-filtro-data', 'end_date'),
    Input("fluviometria-tabs", "active_tab",)
)
def update_fluviometria_main_chart(start_date, end_date, active_tab):

    if active_tab == 'mangue':
        df = Datalake.get('rj-rioaguas.saneamento_drenagem.nivel_reservatorio')
        if start_date is not None:
            df = df[df.data_medicao >= start_date]
        if end_date is not None:
            df = df[df.data_medicao <= end_date]
        fig = px.line(
            df,
            x="data_medicao",
            y="altura_ocupada",
            color="nome_reservatorio",
            title="Altura Ocupada Média por Data para Cada Reservatório"
        ).update_layout(
            xaxis_title='Data',
            yaxis_title='Altura Ocupada (%)',
            legend_title='Reservatório',
        ).update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
            ticklabelmode="period"
        )
    else:
        df = Datalake.get('rj-rioaguas.saneamento_drenagem.qualidade_agua')
        if start_date is not None:
            df = df[df.data_medicao >= start_date]
        if end_date is not None:
            df = df[df.data_medicao <= end_date]
        fig = px.line(
            df,
            x="data_medicao",
            y="IQA",
            title="IQA Médio ao longo do Tempo"
        ).update_layout(
            xaxis_title='Data',
            yaxis_title='Índice de Qualidade da Água (IQA)',
        )

    return fig