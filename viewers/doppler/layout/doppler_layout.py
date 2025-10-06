
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import h5py
import numpy as np
import base64
import io
import re
from scipy.io import wavfile
from scipy import signal
from werkzeug.utils import secure_filename
import plotly.graph_objs as go
import math
import time


# =============================================================================
# CONSTANTS
# =============================================================================

SOUND_SPEED = 343.0  # m/s
DISPLAY_HZ = 25
START_X = -200.0
END_X = 200.0
OBSERVER_X = 0.0
TOTAL_DISTANCE = END_X - START_X

H5_FILENAME = 'viewers/doppler/speed_estimations_NN_1000-200-50-10-1_reg1e-3_lossMSE.h5'

VEHICLE_NAME_MAP = {
    "CitroenC4Picasso": "CitroenC4Picasso",
    "Mazda3": "Mazda3",
    "MercedesAMG550": "MercedesAMG550",
    "NissanQashqai": "NissanQashqai",
    "OpelInsignia": "OpelInsignia",
    "Peugeot3008": "Peugeot3008",
    "Peugeot307": "Peugeot307",
    "RenaultCaptur": "RenaultCaptur",
    "RenaultScenic": "RenaultScenic",
    "VWPassat": "VWPassat"
}

# =============================================================================
# LAYOUTS
# =============================================================================

def create_main_layout():
    """Create the main layout with navigation."""
    return dbc.Container([
        html.H1("Doppler Effect Analyzer", style={'textAlign': 'center'}),
        html.Hr(),
        
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "DETECTION", 
                    href="/doppler-viewer/detection",
                    color="primary", 
                    className="me-2"
                ), 
                width="auto"
            ),
            dbc.Col(
                dbc.Button(
                    "GENERATION", 
                    href="/doppler-viewer/generation",
                    color="secondary"
                ), 
                width="auto"
            ),
        ]),
        
        # dcc.Location(id='url', refresh=False),
        html.Div(id='doppler-content')
    ])


def create_detection_layout():
    """Create the detection page layout for vehicle speed estimation."""
    return dbc.Container([
        html.H2("Vehicle Speed Estimation & Frequency Analysis"),
        html.Hr(),
        
        dbc.Row([
            dbc.Col([
                html.Label("Upload WAV file"),
                dcc.Upload(
                    id='upload-wav',
                    children=html.Div([
                        'Drag and Drop or ', 
                        html.A('Select WAV File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    },
                    multiple=False
                ),
            ])
        ]),
        
        html.Br(),
        
        html.Div(id='file-info', style={'marginBottom': '10px'}),
        html.Div(
            id='max-freq',
            style={
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': 'red',
                'marginBottom': '10px'
            }
        ),
        html.Div(
            id='source-freq-display',
            style={
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': 'green',
                'marginBottom': '20px'
            }
        ),
        
        dcc.Graph(id='waveform-graph')
    ])


def create_generation_layout():
    """Create the generation page layout for Doppler simulator."""
    return dbc.Container([
        html.H2("Doppler Effect Simulator"),
        html.Hr(),

        # Control Panel
        html.Div([
            html.Label("Source frequency (Hz):"),
            dcc.Input(
                id='source-freq',
                type='number',
                value=800,
                step=1,
                style={'marginRight': '12px'}
            ),
            
            html.Label("Speed:"),
            dcc.Input(
                id='speed-input',
                type='number',
                value=60,
                step=1,
                style={'marginRight': '6px'}
            ),
            dcc.Dropdown(
                id='speed-unit',
                options=[
                    {'label': 'km/h', 'value': 'kmh'},
                    {'label': 'm/s', 'value': 'ms'}
                ],
                value='kmh',
                clearable=False,
                style={
                    'width': '80px',
                    'display': 'inline-block',
                    'marginRight': '12px'
                }
            ),
            
            html.Label("Lateral offset (m):"),
            dcc.Input(
                id='lateral-input',
                type='number',
                value=30.0,
                step=0.1,
                style={'marginRight': '12px'}
            ),
            
            html.Button("START / STOP", id='start-button', n_clicks=0, style={'marginRight': '12px'}),
            html.Button("GENERATE AUDIO", id='generate-audio-button', n_clicks=0)
        ], style={'textAlign': 'center', 'padding': '10px'}),

        # Audio player section
        html.Div(id='audio-player-container', style={'textAlign': 'center', 'marginTop': '20px'}),

        # Animation interval
        dcc.Interval(
            id='interval',
            interval=int(1000 / DISPLAY_HZ),
            n_intervals=0,
            disabled=True
        ),

        # Hidden state storage
        html.Div(id='animation-state', children='stopped', style={'display': 'none'}),
        html.Div(id='start-ts', children='0', style={'display': 'none'}),

        # Display information
        html.Div([
            html.Div("Car:", style={'display': 'inline', 'marginRight': '8px'}),
            html.Div(id='car-pos-display', style={'display': 'inline', 'marginRight': '20px'}),
            html.Div("t:", style={'display': 'inline', 'marginRight': '8px'}),
            html.Div(id='time-display', style={'display': 'inline', 'marginRight': '20px'}),
            html.Div("Observed f:", style={'display': 'inline', 'marginRight': '8px'}),
            html.Div(id='freq-display', style={'display': 'inline', 'fontWeight': 'bold'}),
        ], style={'textAlign': 'center', 'paddingTop': '12px'}),

        html.Div(
            id='info',
            style={
                'textAlign': 'center',
                'paddingTop': '12px',
                'fontSize': '14px'
            }
        ),

        # Animation canvas
        html.Div(
            style={
                'height': '300px',
                'position': 'relative',
                'border': '1px solid #ccc',
                'marginTop': '20px'
            },
            children=[
                # Road
                html.Div(style={
                    'position': 'absolute',
                    'left': '0',
                    'right': '0',
                    'top': '40%',
                    'height': '3px',
                    'background': 'black'
                }),
                
                # Observer label
                html.Div(
                    "Observer",
                    style={
                        'position': 'absolute',
                        'left': '50%',
                        'top': '30%',
                        'transform': 'translateX(-50%)'
                    }
                ),
                
                # Car emoji
                html.Div(
                    "🚗",
                    id='car-emoji',
                    style={
                        'position': 'absolute',
                        'left': '10%',
                        'top': '36%',
                        'fontSize': '40px'
                    }
                )
            ]
        )
    ])
