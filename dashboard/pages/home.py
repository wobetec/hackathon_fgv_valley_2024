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
        html.H1('Dashboard - FGV Valley + Fundação Rio-Águas'),
        html.Div(
            [
                html.P('Esse projeto tem por objetivo agregar os dados relacionados a águas no Rio de Janeiro.'),
                html.P('Espera-se com esse projeto, permitir uma visualização ágil e intuitiva dos dados, bem como fomentar a pesquisa, democratizando o acesso aos dados'),
            ]
        ),
    ]
)