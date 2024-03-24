import dash
from dash import html

dash.register_page(
    __name__,
    path='/',
    title='Home',
    name='Home',
    order=1
)

layout = html.Div(
    className='page',
    children=[
        html.H1('This is our Pluviometria page'),
        html.Div('This is our Pluviometria page content.'),
    ]
)