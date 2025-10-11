import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Initialize the app with Bootstrap theme and Bootstrap Icons
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
    ],
    title="Advanced Signal Viewer"
)

server = app.server

# Import page layouts
from pages import home

# Import ECG components and register callbacks
from viewers.ecg.data.loader import ECGDataLoader
from viewers.ecg.models.predictor import ECGPredictor
from viewers.ecg.callbacks import register_all_callbacks
from viewers.ecg.components.layout import create_ecg_layout

from viewers.EEG.callbacks import register_all_callback_eeg
from viewers.EEG.layout import app_layout

from viewers.doppler.layout import create_main_layout
from viewers.doppler.callbacks import doppler_callbacks

from viewers.SAR_Drone.callbacks import register_SAR_drone_callback
from viewers.SAR_Drone.layout import SAR_app_layout

# Initialize ECG components
ecg_data_loader = ECGDataLoader()
ecg_predictor = ECGPredictor()


# Create a single enhanced navbar component
def create_navbar(active_page=None):
    """
    Create an enhanced navigation bar with better styling

    Args:
        active_page (str): The currently active page identifier

    Returns:
        dbc.Navbar: Enhanced navigation bar component
    """
    nav_items = [
        {"label": "Home", "icon": "bi-house-door-fill", "href": "/", "id": "home"},
        {"label": "ECG Viewer", "icon": "bi-heart-pulse-fill", "href": "/ecg-viewer", "id": "ecg"},
        {"label": "EEG Viewer", "icon": "bi-brain", "href": "/EEG-viewer", "id": "eeg"},
        {"label": "Doppler Viewer", "icon": "bi-activity", "href": "/doppler-viewer", "id": "doppler"},
        {"label": "SAR Drone", "icon": "bi-geo-alt-fill", "href": "/SAR-Drone", "id": "sar"},
    ]

    nav_links = []
    for item in nav_items:
        is_active = (active_page == item["id"])
        nav_links.append(
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className=f"{item['icon']} me-2"),
                        item["label"]
                    ],
                    href=item["href"],
                    active=is_active,
                    className="nav-link-custom",
                    style={
                        'fontWeight': '500',
                        'fontSize': '0.95rem',
                        'padding': '0.5rem 1rem',
                        'borderRadius': '8px',
                        'margin': '0 0.2rem',
                        'transition': 'all 0.3s ease',
                        'backgroundColor': 'rgba(255,255,255,0.1)' if is_active else 'transparent',
                    }
                )
            )
        )

    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.A([
                        html.I(className="bi bi-graph-up me-2",
                               style={'fontSize': '1.5rem'}),
                        html.Span("EchoSphere",
                                  style={'fontSize': '1.3rem', 'fontWeight': '700'})
                    ],
                        href="/",
                        style={'textDecoration': 'none', 'color': 'white'})
                ], width="auto"),
                dbc.Col([
                    dbc.Nav(nav_links, navbar=True, className="ms-auto")
                ], width="auto", className="ms-auto")
            ], className="w-100 align-items-center justify-content-between")
        ], fluid=True),
        color="dark",
        dark=True,
        sticky="top",
        className="mb-4 shadow-lg",
        style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'padding': '1rem 0',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }
    )


# Create page layouts WITHOUT individual navbars
ecg_layout = html.Div([
    dbc.Container([
        create_ecg_layout(
            num_records=ecg_data_loader.get_num_records(),
            num_leads=ecg_data_loader.get_num_leads()
        )
    ], fluid=True)
])

eeg_layout = html.Div([
    dbc.Container([
        app_layout()
    ], fluid=True)
])

doppler_layout = html.Div([
    dbc.Container([
        create_main_layout()
    ], fluid=True)
])

sar_drone_layout = html.Div([
    dbc.Container([
        SAR_app_layout()
    ], fluid=True)
])

# Main layout with URL routing and persistent navbar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-container'),
    html.Div(id='page-content')
])


# Routing callback with navbar updates
@app.callback(
    [Output('navbar-container', 'children'),
     Output('page-content', 'children')],
    Input('url', 'pathname'),
)
def display_page(pathname):
    """
    Route to different pages based on URL pathname and update navbar

    Args:
        pathname (str): URL pathname

    Returns:
        tuple: (navbar, page layout)
    """
    if pathname == '/ecg-viewer':
        return create_navbar('ecg'), ecg_layout
    elif pathname == '/EEG-viewer':
        return create_navbar('eeg'), eeg_layout
    elif pathname.startswith('/doppler-viewer'):
        return create_navbar('doppler'), doppler_layout
    elif pathname == '/SAR-Drone':
        return create_navbar('sar'), sar_drone_layout
    elif pathname == '/' or pathname is None:
        return create_navbar('home'), home.layout
    else:
        return create_navbar(None), html.Div([
            dbc.Container([
                html.Div([
                    html.I(className="bi bi-exclamation-triangle-fill text-warning",
                           style={'fontSize': '5rem'}),
                    html.H1("404: Page Not Found", className="mt-4 mb-3"),
                    html.P("The page you're looking for doesn't exist.",
                           className="text-muted mb-4"),
                    dbc.Button([
                        html.I(className="bi bi-house-door me-2"),
                        "Go Home"
                    ], href="/", color="primary", size="lg")
                ], className="text-center", style={'marginTop': '5rem'})
            ])
        ])


register_all_callbacks(app, ecg_data_loader, ecg_predictor)
register_all_callback_eeg(app)
doppler_callbacks(app)
register_SAR_drone_callback(app)

if __name__ == '__main__':
    app.run(debug=False, port=8050)