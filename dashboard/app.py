from dash import Dash, html, dcc, callback, Output, Input, DiskcacheManager, CeleryManager
import dash_bootstrap_components as dbc
import dash
import diskcache
import os

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app, expire=60*5)
else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache, expire=60*5)

app = Dash(
    __name__,
    pages_folder="./pages",
    use_pages=True,
    external_stylesheets=[
        dbc.themes.MATERIA,
        "https://use.fontawesome.com/releases/v6.4.2/css/all.css"
    ],
    background_callback_manager=background_callback_manager,
    # suppress_callback_exceptions=True,
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
