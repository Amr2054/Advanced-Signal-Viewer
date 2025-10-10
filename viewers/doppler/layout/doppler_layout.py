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
# CUSTOM STYLES
# =============================================================================

CARD_STYLE = {
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'borderRadius': '12px',
    'padding': '24px',
    'marginBottom': '20px',
    'background': 'white'
}

HEADER_STYLE = {
    'textAlign': 'center',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'color': 'white',
    'padding': '30px',
    'borderRadius': '12px',
    'marginBottom': '30px',
    'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.2)'
}

BUTTON_STYLE = {
    'borderRadius': '8px',
    'padding': '12px 32px',
    'fontSize': '16px',
    'fontWeight': '600',
    'transition': 'all 0.3s ease',
    'border': 'none',
    'cursor': 'pointer'
}

INPUT_STYLE = {
    'borderRadius': '8px',
    'padding': '10px',
    'border': '2px solid #e0e0e0',
    'fontSize': '14px',
    'transition': 'border-color 0.3s ease'
}

UPLOAD_STYLE = {
    'width': '100%',
    'height': '120px',
    'lineHeight': '120px',
    'borderWidth': '3px',
    'borderStyle': 'dashed',
    'borderRadius': '12px',
    'textAlign': 'center',
    'background': 'linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%)',
    'transition': 'all 0.3s ease',
    'cursor': 'pointer',
    'borderColor': '#667eea'
}

# =============================================================================
# LAYOUTS
# =============================================================================

def create_main_layout():
    """Create the main layout with modern navigation."""
    return dbc.Container([
        # Header
        html.Div([
            html.H1(
                "🎵 DOPPLER EFFECT ANALYZER",
                style={
                    'margin': '0',
                    'fontSize': '42px',
                    'fontWeight': '700',
                    'letterSpacing': '1px'
                }
            ),
            html.P(
                "Analyze and simulate acoustic Doppler effects with precision",
                style={
                    'margin': '10px 0 0 0',
                    'fontSize': '16px',
                    'opacity': '0.9'
                }
            )
        ], style=HEADER_STYLE),
        
        # Navigation Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div("🔍", style={'fontSize': '48px', 'marginBottom': '15px'}),
                        html.H3("Detection", style={'marginBottom': '15px'}),
                        html.P(
                            "Upload audio files to estimate vehicle speed and analyze frequency shifts",
                            style={'color': '#666', 'marginBottom': '20px'}
                        ),
                        dbc.Button(
                            "Launch Detection",
                            href="/doppler-viewer/detection",
                            color="primary",
                            size="lg",
                            style={**BUTTON_STYLE, 'width': '100%'}
                        )
                    ])
                ], style={**CARD_STYLE, 'textAlign': 'center', 'height': '100%'})
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div("🎨", style={'fontSize': '48px', 'marginBottom': '15px'}),
                        html.H3("Generation", style={'marginBottom': '15px'}),
                        html.P(
                            "Simulate Doppler effects in real-time with customizable parameters",
                            style={'color': '#666', 'marginBottom': '20px'}
                        ),
                        dbc.Button(
                            "Launch Simulator",
                            href="/doppler-viewer/generation",
                            color="success",
                            size="lg",
                            style={**BUTTON_STYLE, 'width': '100%'}
                        )
                    ])
                ], style={**CARD_STYLE, 'textAlign': 'center', 'height': '100%'})
            ], md=6)
        ], style={'marginTop': '20px'}),
        
        html.Div(id='doppler-content')
    ], fluid=True, style={'padding': '40px', 'background': '#f5f7fa', 'minHeight': '100vh'})


def create_detection_layout():
    """Create the enhanced detection page layout with audio player controls."""
    return dbc.Container([
        # Page Header
        html.Div([
            html.H2(
                "🔍 Vehicle Speed Estimation & Frequency Analysis",
                style={'margin': '0', 'color': 'white', 'fontSize': '32px'}
            ),
            html.P(
                "Upload a WAV recording to analyze Doppler shift and estimate vehicle speed",
                style={'margin': '10px 0 0 0', 'opacity': '0.9', 'color': 'white'}
            )
        ], style={**HEADER_STYLE, 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}),
        
        # Upload Section
        dbc.Card([
            dbc.CardBody([
                html.H4("📁 Audio File Upload", style={'marginBottom': '20px'}),
                dcc.Upload(
                    id='upload-wav',
                    children=html.Div([
                        html.Div("📤", style={'fontSize': '48px', 'marginBottom': '10px'}),
                        html.Div("Drag and Drop or ", style={'display': 'inline', 'fontSize': '16px'}),
                        html.A("Select WAV File", style={'color': '#667eea', 'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.Div("Supported format: WAV (uncompressed audio)", 
                                style={'marginTop': '10px', 'fontSize': '12px', 'color': '#888'})
                    ], style={'textAlign': 'center'}),
                    style=UPLOAD_STYLE,
                    multiple=False
                ),
            ])
        ], style=CARD_STYLE),
        
        # Audio Player Section
        html.Div(id='audio-player-section', children=[], style={'marginBottom': '20px'}),
        
        # Results Section
        dbc.Card([
            dbc.CardBody([
                html.H4("📊 Analysis Results", style={'marginBottom': '20px'}),
                
                # File Info
                html.Div(id='file-info', style={
                    'padding': '12px',
                    'background': '#f8f9fa',
                    'borderRadius': '8px',
                    'marginBottom': '15px',
                    'fontSize': '14px'
                }),
                
                # Key Metrics Row
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div("Predicted Velocity", style={
                                'fontSize': '12px',
                                'color': '#888',
                                'textTransform': 'uppercase',
                                'marginBottom': '5px',
                                'fontWeight': '600'
                            }),
                            html.Div(id='max-freq', style={
                                'fontSize': '28px',
                                'fontWeight': 'bold',
                                'color': '#e74c3c'
                            })
                        ], style={
                            'padding': '20px',
                            'background': '#fff5f5',
                            'borderRadius': '8px',
                            'textAlign': 'center',
                            'border': '2px solid #e74c3c'
                        })
                    ], md=6),
                    
                    dbc.Col([
                        html.Div([
                            html.Div("Predicted Frequency", style={
                                'fontSize': '12px',
                                'color': '#888',
                                'textTransform': 'uppercase',
                                'marginBottom': '5px',
                                'fontWeight': '600'
                            }),
                            html.Div(id='source-freq-display', style={
                                'fontSize': '28px',
                                'fontWeight': 'bold',
                                'color': '#27ae60'
                            })
                        ], style={
                            'padding': '20px',
                            'background': '#f0fff4',
                            'borderRadius': '8px',
                            'textAlign': 'center',
                            'border': '2px solid #27ae60'
                        })
                    ], md=6)
                ], style={'marginBottom': '20px'}),
                
                # Waveform Graph
                dcc.Graph(
                    id='waveform-graph',
                    config={'displayModeBar': True, 'displaylogo': False},
                    style={'borderRadius': '8px', 'overflow': 'hidden'}
                )
            ])
        ], style=CARD_STYLE),
        
        # Hidden storage for audio data
        html.Div(id='audio-data-store', style={'display': 'none'}),
        
        # Back Button
        dbc.Button(
            "← Back to Home",
            href="/doppler-viewer",
            color="secondary",
            style={**BUTTON_STYLE, 'marginTop': '20px'}
        )
    ], fluid=True, style={'padding': '40px', 'background': '#f5f7fa', 'minHeight': '100vh'})


def create_generation_layout():
    """Create the enhanced generation page layout."""
    return dbc.Container([
        # Page Header
        html.Div([
            html.H2(
                "🎨 Doppler Effect Simulator",
                style={'margin': '0', 'color': 'white', 'fontSize': '32px'}
            ),
            html.P(
                "Generate and visualize Doppler-shifted audio in real-time",
                style={'margin': '10px 0 0 0', 'opacity': '0.9', 'color': 'white'}
            )
        ], style={**HEADER_STYLE, 'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'}),
        
        # Control Panel
        dbc.Card([
            dbc.CardBody([
                html.H4("⚙️ Simulation Parameters", style={'marginBottom': '25px'}),
                
                dbc.Row([
                    # Source Frequency
                    dbc.Col([
                        html.Label("Source Frequency", style={
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#333'
                        }),
                        dbc.InputGroup([
                            dcc.Input(
                                id='source-freq',
                                type='number',
                                value=800,
                                step=1,
                                style={**INPUT_STYLE, 'flex': '1'}
                            ),
                            dbc.InputGroupText("Hz")
                        ])
                    ], md=3),
                    
                    # Vehicle Speed
                    dbc.Col([
                        html.Label("Vehicle Speed", style={
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#333'
                        }),
                        dbc.InputGroup([
                            dcc.Input(
                                id='speed-input',
                                type='number',
                                value=60,
                                step=1,
                                style={**INPUT_STYLE, 'flex': '1'}
                            ),
                            dcc.Dropdown(
                                id='speed-unit',
                                options=[
                                    {'label': 'km/h', 'value': 'kmh'},
                                    {'label': 'm/s', 'value': 'ms'}
                                ],
                                value='kmh',
                                clearable=False,
                                style={'width': '100px', 'borderRadius': '0 8px 8px 0'}
                            )
                        ])
                    ], md=3),
                    
                    # Lateral Offset
                    dbc.Col([
                        html.Label("Lateral Offset", style={
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#333'
                        }),
                        dbc.InputGroup([
                            dcc.Input(
                                id='lateral-input',
                                type='number',
                                value=30.0,
                                step=0.1,
                                style={**INPUT_STYLE, 'flex': '1'}
                            ),
                            dbc.InputGroupText("m")
                        ])
                    ], md=3),
                    
                    # Control Buttons
                    dbc.Col([
                        html.Label("Controls", style={
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            'display': 'block',
                            'color': '#333'
                        }),
                        dbc.ButtonGroup([
                            dbc.Button(
                                "▶ Start",
                                id='start-button',
                                color="primary",
                                n_clicks=0,
                                style={'borderRadius': '8px 0 0 8px'}
                            ),
                            dbc.Button(
                                "🎵 Generate",
                                id='generate-audio-button',
                                color="success",
                                n_clicks=0,
                                style={'borderRadius': '0 8px 8px 0'}
                            )
                        ], style={'width': '100%'})
                    ], md=3)
                ])
            ])
        ], style=CARD_STYLE),
        
        # Audio Player
        html.Div(id='audio-player-container', style={
            'textAlign': 'center',
            'marginTop': '20px',
            'marginBottom': '20px'
        }),
        
        # Real-time Metrics
        dbc.Card([
            dbc.CardBody([
                html.H4("📡 Real-Time Metrics", style={'marginBottom': '20px'}),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div("Vehicle Position", style={
                                'fontSize': '12px',
                                'color': '#888',
                                'textTransform': 'uppercase',
                                'marginBottom': '5px'
                            }),
                            html.Div(id='car-pos-display', style={
                                'fontSize': '24px',
                                'fontWeight': 'bold',
                                'color': '#3498db'
                            })
                        ], style={'textAlign': 'center'})
                    ], md=4),
                    
                    dbc.Col([
                        html.Div([
                            html.Div("Elapsed Time", style={
                                'fontSize': '12px',
                                'color': '#888',
                                'textTransform': 'uppercase',
                                'marginBottom': '5px'
                            }),
                            html.Div(id='time-display', style={
                                'fontSize': '24px',
                                'fontWeight': 'bold',
                                'color': '#9b59b6'
                            })
                        ], style={'textAlign': 'center'})
                    ], md=4),
                    
                    dbc.Col([
                        html.Div([
                            html.Div("Observed Frequency", style={
                                'fontSize': '12px',
                                'color': '#888',
                                'textTransform': 'uppercase',
                                'marginBottom': '5px'
                            }),
                            html.Div(id='freq-display', style={
                                'fontSize': '24px',
                                'fontWeight': 'bold',
                                'color': '#e67e22'
                            })
                        ], style={'textAlign': 'center'})
                    ], md=4)
                ])
            ])
        ], style=CARD_STYLE),
        
        # Animation Canvas
        dbc.Card([
            dbc.CardBody([
                html.H4("🎬 Animation", style={'marginBottom': '20px'}),
                
                html.Div(
                    style={
                        'height': '300px',
                        'position': 'relative',
                        'background': 'linear-gradient(to bottom, #87CEEB 0%, #E0F6FF 50%, #90EE90 50%, #C8E6C9 100%)',
                        'borderRadius': '12px',
                        'overflow': 'hidden',
                        'boxShadow': 'inset 0 2px 8px rgba(0,0,0,0.1)'
                    },
                    children=[
                        # Road
                        html.Div(style={
                            'position': 'absolute',
                            'left': '0',
                            'right': '0',
                            'top': '50%',
                            'height': '60px',
                            'background': '#555',
                            'transform': 'translateY(-50%)'
                        }),
                        
                        # Road markings
                        html.Div(style={
                            'position': 'absolute',
                            'left': '0',
                            'right': '0',
                            'top': '50%',
                            'height': '4px',
                            'background': 'repeating-linear-gradient(to right, white 0px, white 40px, transparent 40px, transparent 80px)',
                            'transform': 'translateY(-50%)'
                        }),
                        
                        # Observer
                        html.Div([
                            html.Div("👤", style={'fontSize': '40px', 'marginBottom': '5px'}),
                            html.Div("Observer", style={
                                'fontSize': '14px',
                                'fontWeight': 'bold',
                                'color': '#333',
                                'background': 'rgba(255,255,255,0.9)',
                                'padding': '4px 12px',
                                'borderRadius': '12px',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                            })
                        ], style={
                            'position': 'absolute',
                            'left': '50%',
                            'top': '20%',
                            'transform': 'translateX(-50%)',
                            'textAlign': 'center'
                        }),
                        
                        # Car
                        html.Div(
                            "🚗",
                            id='car-emoji',
                            style={
                                'position': 'absolute',
                                'left': '10%',
                                'top': '50%',
                                'fontSize': '50px',
                                'transform': 'translateY(-50%)',
                                'filter': 'drop-shadow(2px 2px 4px rgba(0,0,0,0.3))',
                                'transition': 'left 0.04s linear'
                            }
                        )
                    ]
                ),
                
                # Info Display
                html.Div(
                    id='info',
                    style={
                        'textAlign': 'center',
                        'marginTop': '15px',
                        'fontSize': '14px',
                        'color': '#666',
                        'fontStyle': 'italic'
                    }
                )
            ])
        ], style=CARD_STYLE),
        
        # Hidden components
        dcc.Interval(
            id='interval',
            interval=int(1000 / DISPLAY_HZ),
            n_intervals=0,
            disabled=True
        ),
        html.Div(id='animation-state', children='stopped', style={'display': 'none'}),
        html.Div(id='start-ts', children='0', style={'display': 'none'}),
        
        # Back Button
        dbc.Button(
            "← Back to Home",
            href="/doppler-viewer",
            color="secondary",
            style={**BUTTON_STYLE, 'marginTop': '20px'}
        )
    ], fluid=True, style={'padding': '40px', 'background': '#f5f7fa', 'minHeight': '100vh'})