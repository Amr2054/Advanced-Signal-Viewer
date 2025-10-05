"""
Advanced Signal Viewer - Main Application
Multi-page Dash application for viewing different types of physiological signals
"""
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Initialize the app with Bootstrap theme
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Advanced Signal Viewer"
)

server = app.server

# Main layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

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
# print("🔧 Initializing ECG components...")
ecg_data_loader = ECGDataLoader()
ecg_predictor = ECGPredictor()

# Create ECG layout
ecg_layout = html.Div([
    # Navigation bar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand("❤️ ECG Viewer", className="ms-2")
                ]),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="/", className="text-light")),
                        dbc.NavItem(dbc.NavLink("ECG Viewer", href="/ecg-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("EEG Viewer", href="/EEG-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("Doppler Viewer", href="/doppler-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("SAR - Drone Viewer", href="/SAR-Drone", active=True, className="text-light")),
                    ], navbar=True)
                ], className="ms-auto")
            ], className="w-100 align-items-center")
        ], fluid=True),
        color="danger",
        dark=True,
        className="mb-4"
    ),
    # ECG Viewer content
    dbc.Container([
        create_ecg_layout(
            num_records=ecg_data_loader.get_num_records(),
            num_leads=ecg_data_loader.get_num_leads()
        )
    ], fluid=True)
])

eeg_layout = html.Div([
    # Navigation bar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand("EEG Viewer", className="ms-2")
                ]),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="/", className="text-light")),
                        dbc.NavItem(dbc.NavLink("ECG Viewer", href="/ecg-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("EEG Viewer", href="/EEG-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("Doppler Viewer", href="/doppler-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("SAR - Drone Viewer", href="/SAR-Drone", active=True, className="text-light")),
                    ], navbar=True)
                ], className="ms-auto")
            ], className="w-100 align-items-center")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    ),

    dbc.Container([
        app_layout()
    ], fluid=True)

])

doppler_layout = html.Div([
    # Navigation bar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand("Doppler Signal Viewer", className="ms-2")
                ]),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="/", className="text-light")),
                        dbc.NavItem(dbc.NavLink("ECG Viewer", href="/ecg-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("EEG Viewer", href="/EEG-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("Doppler Viewer", href="/doppler-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("SAR - Drone Viewer", href="/SAR-Drone", active=True, className="text-light")),
                    ], navbar=True)
                ], className="ms-auto")
            ], className="w-100 align-items-center")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    ),

    dbc.Container([
        create_main_layout()
    ], fluid=True)

])

sar_drone_layout = html.Div([
    # Navigation bar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand("SAR - Drone Viewer", className="ms-2")
                ]),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="/", className="text-light")),
                        dbc.NavItem(dbc.NavLink("ECG Viewer", href="/ecg-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("EEG Viewer", href="/EEG-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("Doppler Viewer", href="/doppler-viewer", active=True, className="text-light")),
                        dbc.NavItem(dbc.NavLink("SAR - Drone Viewer", href="/SAR-Drone", active=True, className="text-light")),
                    ], navbar=True)
                ], className="ms-auto")
            ], className="w-100 align-items-center")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    ),

    dbc.Container([
        SAR_app_layout()
    ], fluid=True)

])

# Register ECG callbacks BEFORE routing callback
# print("📡 Registering ECG callbacks...")

# print(f"✅ Callbacks registered: {len(app.callback_map)}")
#
#
# print("📡 Registering EEG callbacks...")

# print(f"✅ Callbacks registered: {len(app.callback_map)}")

# Routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def display_page(pathname):
    """
    Route to different pages based on URL pathname

    Args:
        pathname (str): URL pathname

    Returns:
        layout: Page layout component
    """
    if pathname == '/ecg-viewer':
        return ecg_layout
    elif pathname == '/EEG-viewer':
        return eeg_layout
    elif pathname.startswith('/doppler-viewer'):
        return doppler_layout
    elif pathname == '/SAR-Drone':
        return sar_drone_layout
    elif pathname == '/' or pathname is None:
        return home.layout
    else:
        return html.Div([
            html.H1("404: Page Not Found", className="text-center mt-5"),
            html.P("The page you're looking for doesn't exist."),
            dbc.Button("Go Home", href="/", color="primary", className="mt-3")
        ], className="container")

register_all_callbacks(app, ecg_data_loader, ecg_predictor)
register_all_callback_eeg(app)
doppler_callbacks(app)
register_SAR_drone_callback(app)


if __name__ == '__main__':
    # print("\n🚀 Starting Advanced Signal Viewer...")
    # print("📍 Visit: http://localhost:8050/")
    app.run(debug=True, port=8050)