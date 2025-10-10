import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from dash import dcc, html
from viewers.EEG.Data_helper import *
from viewers.EEG.visualize_utils import *

# Path (change on your device)
Path = 'viewers/EEG/'

# -------- Load Configs --------
with open(f"{Path}config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

#Constants-------------------
AVAILABLE_COLORMAPS = config['AVAILABLE_COLORMAPS']
DEFAULT_COLORMAP = config['DEFAULT_COLORMAP']
#-----------------------------

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
        html.H1("EEG Signal Viewer - Dynamic Analysis", style=custom_styles['header']),

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
                    dcc.Slider(
                        id="window-start",
                        value=0,
                        min=0,
                        max = 1000,
                        step=1,
                        marks={0: '0x', 15: '15x', 50: '50x', 300: '300x', 500: '500x'}
                    ),
                ], style={'width': '15%', 'display': 'inline-block', 'marginRight': '2%'}),

                html.Div([
                    html.Label("Window Length (s)", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id="window-length",
                        value=10,
                        min=1,
                        max=60,
                        step=1,
                        marks={1: '1x', 10: '10x', 25: '25x', 40: '40x', 55: '55x'}
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
            
            html.Div([
                html.Label("Colormap:", style={'fontWeight': '600'}),
                dcc.Dropdown(
                    id="ecg-colormap-select",
                    options=[{"label": cm, "value": cm} for cm in AVAILABLE_COLORMAPS],
                    value=DEFAULT_COLORMAP
                ),
            ], style={'width': '23%', 'display': 'inline-block'})
            
        ], style={'marginBottom': '20px'}),

        dcc.Graph(id="crp-plot"),

        # XOR Graph Section
        html.Hr(style={'marginTop': '30px', 'marginBottom': '30px'}),
        html.Div([
            html.H3("XOR Graph Analysis", style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.Label("Channel", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id="xor-channel",
                        options=[{"label": ch, "value": i} for i, ch in enumerate(CH_LABELS)],
                        value=0,
                        clearable=False
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
                
                html.Div([
                    html.Label("Chunk Width (s)", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id="chunk-width",
                        min=1,
                        max=100,
                        value=5,
                        marks={1: '1x', 10: '10x', 25: '25x', 40: '40x', 55: '55x'},
                        step=1,
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                
                html.Div([
                    html.Label("Signal Time (s)", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id="Time",
                        min=1,
                        max=1000,
                        value=10,
                        marks={1: '1x', 10: '10x', 25: '25x', 100: '100x', 550: '550x'},
                        step=1,
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("XOR Threshold", style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id="threshold",
                        value=20,
                        min=1,
                        max=200,
                        step=1,
                        marks={1: '1x', 10: '10x', 25: '25x', 40: '40x', 55: '55x'}
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
            ], style={'marginBottom': '20px'}),
            
            dcc.Graph(id="xor-graph"),
        ]),
        
        
        # Store components
        dcc.Store(id="data-loaded", data=False),
        dcc.Store(id="playback-state", data={'playing': False, 'current_time': 0}),
        dcc.Store(id="signal-duration", data=0),

    ], style=custom_styles['container'])