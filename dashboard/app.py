from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
import os


app = Dash(
    __name__,
    pages_folder="./pages",
    use_pages=True,
    external_stylesheets=[
        dbc.themes.MATERIA,
        "https://use.fontawesome.com/releases/v6.4.2/css/all.css"
    ]
)

sidebar = html.Div(
    id='sidebar',
    children=[
        html.Div(
            id='sidebar-title',
            children=[
                html.Img(src='./assets/images/logo_prefeitura.png')
            ]
        ),
        dbc.Nav(
            id='sidebar-nav',
            children=[
                dbc.NavLink(
                    html.Div(page["name"]),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        )
    ]
)

content = html.Div(
    id='content',
    children=[
        dash.page_container
    ]
)

app.layout = html.Div(
    id='app-layout',
    children=[
        sidebar,
        content,
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
