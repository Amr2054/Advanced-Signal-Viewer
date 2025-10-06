import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from dash import dcc, html
from viewers.EEG.Data_helper import *
from viewers.EEG.visualize_utils import *

# Custom CSS styles
custom_styles = {
    'container': {
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '20px',
        'fontFamily': '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
        'backgroundColor': '#f5f7fa',
        'minHeight': '100vh',
    },
    'header': {
        'textAlign': 'center',
        'color': '#2c3e50',
        'fontSize': '2.5em',
        'fontWeight': '600',
        'marginBottom': '30px',
    },
    'upload': {
        'width': '100%',
        'height': '120px',
        'lineHeight': '120px',
        'borderWidth': '2px',
        'borderStyle': 'dashed',
        'borderColor': '#3498db',
        'borderRadius': '8px',
        'textAlign': 'center',
        'margin': '20px 0',
        'backgroundColor': '#ffffff',
        'cursor': 'pointer',
        'transition': 'border-color 0.3s ease, background-color 0.3s ease',
    },
    'uploadText': {
        'color': '#34495e',
        'fontSize': '1.2em',
        'fontWeight': '500',
    },
    'link': {
        'color': '#3498db',
        'textDecoration': 'none',
        'fontWeight': '600',
    },
    'output': {
        'marginTop': '20px',
        'padding': '15px',
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'color': '#2c3e50',
        'fontSize': '1.1em',
    },
    'controlPanel': {
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'padding': '20px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    }
}


# layout
def app_layout():
    return html.Div([
        html.H1("EEG Signal Viewer", style=custom_styles['header']),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select ZIP File', style=custom_styles['link'])
            ], style=custom_styles['uploadText']),
            multiple=False,
            accept='.zip',
            style=custom_styles['upload']
        ),

        dcc.Loading(
            id="loading",
            type="circle",
            children=html.Div(id='output-message', style=custom_styles['output']),
        ),

        # Summary plot
        dcc.Graph(id="summary-plot"),

        # Continuous Viewer Section
        html.Div([
            html.H3("Continuous Signal Viewer", style={'textAlign': 'center', 'marginTop': '30px'}),
            html.Div([
                html.Div([
                    html.Label("Channel", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id="continuous-channel",
                        options=[{"label": ch, "value": i} for i, ch in enumerate(CH_LABELS)],
                        value=0,
                        clearable=False
                    ),
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Label("Window Start (s)", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id="window-start",
                        type="number",
                        value=0,
                        min=0,
                        step=1,
                        style={'width': '100%'}
                    ),
                ], style={'width': '15%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Label("Window Length (s)", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id="window-length",
                        type="number",
                        value=10,
                        min=1,
                        max=60,
                        step=1,
                        style={'width': '100%'}
                    ),
                ], style={'width': '15%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Label("Playback Speed", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id="playback-speed",
                        min=0.5,
                        max=5,
                        value=1,
                        marks={0.5: '0.5x', 1: '1x', 2: '2x', 3: '3x', 5: '5x'},
                        step=0.5,
                    ),
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Button('Play', id='play-button', n_clicks=0, style={'marginRight': '10px'}),
                    html.Button('Stop', id='stop-button', n_clicks=0),
                    dcc.Checklist(
                        id="show-predictions",
                        options=[{"label": "Show Seizures", "value": "show"}],
                        value=["show"],
                        inline=True,
                        style={'marginTop': '10px'}
                    ),
                ], style={'width': '20%', 'display': 'inline-block'}),
            ], style=custom_styles['controlPanel']),

            dcc.Graph(id="continuous-viewer"),
            dcc.Interval(id='interval-component', interval=1000, disabled=True),
        ]),

        # Segment viewer controls
        html.Div([
            html.H3("Segment Viewer", style={'textAlign': 'center', 'marginTop': '30px'}),
            html.Div([
                html.Div([
                    html.Label("Select Segment", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id="segment-dropdown",
                        options=[],
                        value=0,
                        clearable=False,
                        style={'marginBottom': '15px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Label("Select Channel", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id="channel-dropdown",
                        options=[{"label": ch, "value": i} for i, ch in enumerate(CH_LABELS)],
                        value=0,
                        clearable=False,
                        style={'marginBottom': '15px'}
                    ),
                ], style={'width': '48%', 'display': 'inline-block'}),
            ]),
        ]),

        # Segment plots
        dcc.Graph(id="segment-plots"),

        # CRP Section
        html.Hr(style={'marginTop': '30px', 'marginBottom': '30px'}),
        html.H3("Cross Recurrence Analysis (Entire Signal)", style={'textAlign': 'center'}),

        html.Div([
            html.Div([
                html.Label("Select Channel 1", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="channel-1-dropdown",
                    options=[{"label": ch, "value": i} for i, ch in enumerate(CH_LABELS)],
                    value=0,
                    clearable=False
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),

            html.Div([
                html.Label("Select Channel 2", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="channel-2-dropdown",
                    options=[{"label": ch, "value": i} for i, ch in enumerate(CH_LABELS)],
                    value=1,
                    clearable=False
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),
        ], style={'marginBottom': '20px'}),

        dcc.Graph(id="crp-plot"),

        # Store components
        dcc.Store(id="data-loaded", data=False),
        dcc.Store(id="playback-state", data={'playing': False, 'current_time': 0}),
        dcc.Store(id="signal-duration", data=0),

    ], style=custom_styles['container'])