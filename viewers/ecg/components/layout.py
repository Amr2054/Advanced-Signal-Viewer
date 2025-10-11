from dash import dcc, html
import dash_bootstrap_components as dbc
from viewers.ecg.config import (
    DEFAULT_SELECTED_CHANNELS,
    DEFAULT_PHASE_SPACE_CHANNEL_1,
    DEFAULT_PHASE_SPACE_CHANNEL_2,
    CONTINUOUS_DEFAULT_WINDOW,
    CONTINUOUS_MIN_WINDOW,
    CONTINUOUS_MAX_WINDOW,
    CONTINUOUS_DEFAULT_SPEED,
    CONTINUOUS_MIN_SPEED,
    CONTINUOUS_MAX_SPEED,
    XOR_CHUNKS_DEFAULT_PERIOD,
    XOR_CHUNKS_MIN_PERIOD,
    XOR_CHUNKS_MAX_PERIOD,
    XOR_CHUNKS_DEFAULT_DURATION,
    POLAR_DEFAULT_WINDOW,
    POLAR_MIN_WINDOW,
    POLAR_MAX_WINDOW,
    AVAILABLE_COLORMAPS,
    DEFAULT_COLORMAP
)

ECG_LEAD_NAMES = [
    'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
    'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
]


def create_ecg_layout(num_records, num_leads):
    """Create ECG viewer layout with right sidebar"""

    return html.Div([
        # Main container with flexbox
        html.Div([

            # LEFT SIDE - Main visualization area
            html.Div([
                # Header
                html.H2("ECG Signal Viewer",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '20px',
                            'color': '#2c3e50',
                            'fontWeight': 'bold'
                        }),

                # BPM and Diagnosis outputs
                html.Div([
                    html.Div(id="ecg-bpm-output",
                             className="alert alert-success",
                             style={
                                 "fontSize": "16px",
                                 "marginBottom": "10px",
                                 "padding": "10px"
                             }),
                    html.Div(id="ecg-diagnosis-output",
                             className="alert alert-info",
                             style={
                                 "fontSize": "16px",
                                 "marginBottom": "20px",
                                 "padding": "10px"
                             }),
                ]),

                # Main graph
                dcc.Graph(
                    id='ecg-graph',
                    config={'displayModeBar': True},
                    style={
                        'height': '70vh',
                        'border': '2px solid #dee2e6',
                        'borderRadius': '8px',
                        'backgroundColor': 'white'
                    }
                ),

                # Secondary graph for polar mode (time domain view)
                html.Div([
                    html.H5("Time Domain View",
                            style={
                                'color': '#2c3e50',
                                'marginTop': '20px',
                                'marginBottom': '10px'
                            }),
                    dcc.Graph(
                        id='ecg-polar-time-graph',
                        config={'displayModeBar': True},
                        style={
                            'height': '25vh',
                            'border': '2px solid #dee2e6',
                            'borderRadius': '8px',
                            'backgroundColor': 'white'
                        }
                    ),
                ], id='ecg-polar-time-view', style={'display': 'none'}),

            ], style={
                'flex': '1',
                'padding': '20px',
                'overflowY': 'auto',
                'backgroundColor': '#f8f9fa'
            }),

            # RIGHT SIDE - Control sidebar
            html.Div([
                html.Div([

                    # === DATA SOURCE SELECTION ===
                    html.Div([
                        html.H5("📁 Data Source",
                                style={
                                    'color': '#2c3e50',
                                    'marginBottom': '15px',
                                    'fontWeight': 'bold'
                                }),

                        dcc.RadioItems(
                            id='ecg-data-source-select',
                            options=[
                                {'label': ' Preloaded Data', 'value': 'preloaded'},
                                {'label': ' Upload File', 'value': 'upload'}
                            ],
                            value='preloaded',
                            labelStyle={
                                'display': 'block',
                                'padding': '8px',
                                'cursor': 'pointer'
                            }
                        ),

                        # Upload component
                        html.Div([
                            dcc.Upload(
                                id='ecg-upload-data',
                                children=html.Div([
                                    '📤 Drag and Drop or ',
                                    html.A('Select ZIP/NPZ File', style={'color': '#007bff'})
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '8px',
                                    'textAlign': 'center',
                                    'backgroundColor': '#f8f9fa',
                                    'cursor': 'pointer',
                                    'marginTop': '10px'
                                },
                                multiple=False
                            ),
                            html.Div(id='ecg-upload-status',
                                     style={
                                         'marginTop': '10px',
                                         'fontSize': '12px',
                                         'color': '#666'
                                     })
                        ], id='ecg-upload-container', style={'display': 'none'}),

                    ], style={
                        'padding': '15px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),

                    # === RECORD SELECTION ===
                    html.Div([
                        html.H5("Record Selection",
                                style={
                                    'color': '#2c3e50',
                                    'marginBottom': '10px',
                                    'fontWeight': 'bold'
                                }),
                        dcc.Dropdown(
                            id="ecg-record-select",
                            options=[{"label": f"Record {i}", "value": i} for i in range(num_records)],
                            value=None,
                            placeholder="Select a record...",
                            clearable=False,
                            style={'width': '100%'}
                        ),
                    ], style={
                        'padding': '15px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),

                    # === LEAD SELECTION ===
                    html.Div([
                        html.H5("Lead Selection",
                                style={
                                    'color': '#2c3e50',
                                    'marginBottom': '10px',
                                    'fontWeight': 'bold'
                                }),
                        html.Div([
                            dcc.Checklist(
                                id='ecg-channel-select',
                                options=[
                                    {'label': f' {ECG_LEAD_NAMES[i]}', 'value': i}
                                    for i in range(min(num_leads, 12))
                                ],
                                value=DEFAULT_SELECTED_CHANNELS,
                                labelStyle={
                                    'display': 'inline-block',
                                    'margin': '4px',
                                    'padding': '6px 10px',
                                    'border': '2px solid #3498db',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'backgroundColor': '#ecf0f1',
                                    'fontSize': '12px',
                                    'fontWeight': '500'
                                },
                                inputStyle={
                                    'marginRight': '5px'
                                }
                            )
                        ], style={
                            'maxHeight': '200px',
                            'overflowY': 'auto',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'borderRadius': '5px'
                        })
                    ], style={
                        'padding': '15px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),

                    # === VISUALIZATION MODE ===
                    html.Div([
                        html.H5("Visualization Mode",
                                style={
                                    'color': '#2c3e50',
                                    'marginBottom': '10px',
                                    'fontWeight': 'bold'
                                }),
                        dcc.RadioItems(
                            id='ecg-mode-select',
                            options=[
                                {'label': ' Static ', 'value': 'static'},
                                {'label': ' Continuous ', 'value': 'continuous'},
                                {'label': ' XOR ', 'value': 'xor_chunks'},
                                {'label': ' Polar ', 'value': 'polar_new'},
                                {'label': '  Cross Recurrence ', 'value': 'phase_space'},
                            ],
                            value='static',
                            labelStyle={
                                'display': 'block',
                                'padding': '8px 12px',
                                'margin': '5px 0',
                                'border': '2px solid #e0e0e0',
                                'borderRadius': '6px',
                                'cursor': 'pointer',
                                'backgroundColor': '#f8f9fa',
                                'fontSize': '13px'
                            }
                        )
                    ], style={
                        'padding': '15px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),

                    # === MODE-SPECIFIC CONTROLS ===

                    # Continuous Controls
                    html.Div([
                        html.H6("⚙️ Continuous Controls",
                                style={'color': '#2c3e50', 'marginBottom': '10px'}),
                        html.Div([
                            html.Button("▶ Play", id="ecg-continuous-play-pause",
                                        className="btn btn-success btn-sm",
                                        style={'width': '48%', 'marginRight': '4%'}),
                            html.Button("⏮ Reset", id="ecg-continuous-reset",
                                        className="btn btn-secondary btn-sm",
                                        style={'width': '48%'}),
                        ], style={'marginBottom': '10px'}),
                        html.Div([
                            html.Button("◀ Pan Left", id="ecg-continuous-pan-left",
                                        className="btn btn-info btn-sm",
                                        style={'width': '48%', 'marginRight': '4%'}),
                            html.Button("Pan Right ▶", id="ecg-continuous-pan-right",
                                        className="btn btn-info btn-sm",
                                        style={'width': '48%'}),
                        ], style={'marginBottom': '15px'}),

                        html.Label(["Speed: ", html.Span(id="ecg-continuous-speed-display",
                                                         style={'color': '#3498db', 'fontWeight': 'bold'})]),
                        dcc.Slider(id='ecg-continuous-speed',
                                   min=CONTINUOUS_MIN_SPEED,
                                   max=CONTINUOUS_MAX_SPEED,
                                   step=0.1,
                                   value=CONTINUOUS_DEFAULT_SPEED,
                                   marks={0.1: '0.1x', 1.0: '1x', 2.0: '2x', 5.0: '5x'}),

                        html.Label(["Zoom: ", html.Span(id="ecg-continuous-zoom-display",
                                                        style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-continuous-zoom',
                                   min=CONTINUOUS_MIN_WINDOW,
                                   max=CONTINUOUS_MAX_WINDOW,
                                   step=0.5,
                                   value=CONTINUOUS_DEFAULT_WINDOW,
                                   marks={1: '1s', 10: '10s', 30: '30s'}),

                        html.Label(["Position: ", html.Span(id="ecg-continuous-position-display",
                                                            style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-continuous-position',
                                   min=0, max=100, step=0.1, value=0, marks={}),
                    ], id="ecg-continuous-controls", style={'display': 'none', 'padding': '15px',
                                                            'backgroundColor': 'white', 'borderRadius': '8px',
                                                            'marginBottom': '20px',
                                                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                    # XOR Chunks Controls
                    html.Div([
                        html.H6("⚙️ XOR Controls",
                                style={'color': '#2c3e50', 'marginBottom': '10px'}),

                        html.Label("Channel:", style={'fontWeight': '600'}),
                        dcc.Dropdown(
                            id="ecg-xor-chunks-channel",
                            options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i}
                                     for i in range(min(num_leads, 12))],
                            value=0
                        ),

                        html.Label(["Chunk Period: ",
                                    html.Span(id="ecg-xor-chunk-period-display",
                                              style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-xor-chunk-period',
                                   min=XOR_CHUNKS_MIN_PERIOD,
                                   max=XOR_CHUNKS_MAX_PERIOD,
                                   step=0.1,
                                   value=XOR_CHUNKS_DEFAULT_PERIOD,
                                   marks={0.2: '0.2s', 1: '1s', 3: '3s', 5: '5s'}),

                        html.Label(["Duration: ",
                                    html.Span(id="ecg-xor-duration-display",
                                              style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-xor-duration',
                                   min=2, max=30, step=1,
                                   value=XOR_CHUNKS_DEFAULT_DURATION,
                                   marks={5: '5s', 10: '10s', 20: '20s', 30: '30s'}),

                        html.Label(["Threshold: ",
                                    html.Span(id="ecg-xor-threshold-display",
                                              style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-xor-chunks-threshold',
                                   min=0.01, max=0.5, step=0.01, value=0.05,
                                   marks={0.01: '0.01', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),
                    ], id="ecg-xor-chunks-controls", style={'display': 'none', 'padding': '15px',
                                                            'backgroundColor': 'white', 'borderRadius': '8px',
                                                            'marginBottom': '20px',
                                                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                    # Polar Controls
                    html.Div([
                        html.H6("⚙️ Polar Controls",
                                style={'color': '#2c3e50', 'marginBottom': '10px'}),

                        html.Label("Channel:", style={'fontWeight': '600'}),
                        dcc.Dropdown(
                            id="ecg-polar-channel",
                            options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i}
                                     for i in range(min(num_leads, 12))],
                            value=0
                        ),

                        html.Label(["Window: ",
                                    html.Span(id="ecg-polar-window-display",
                                              style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-polar-window',
                                   min=POLAR_MIN_WINDOW,
                                   max=POLAR_MAX_WINDOW,
                                   step=0.5,
                                   value=POLAR_DEFAULT_WINDOW,
                                   marks={1: '1s', 5: '5s', 10: '10s', 20: '20s'}),

                        html.Label("Display Mode:",
                                   style={'fontWeight': '600', 'marginTop': '10px'}),
                        dcc.RadioItems(
                            id='ecg-polar-mode',
                            options=[
                                {'label': ' Latest', 'value': 'latest'},
                                {'label': ' Cumulative', 'value': 'cumulative'}
                            ],
                            value='latest',
                            inline=True
                        ),

                        html.Div([
                            html.Button("▶ Play", id="ecg-polar-play-pause",
                                        className="btn btn-success btn-sm",
                                        style={'width': '48%', 'marginRight': '4%', 'marginTop': '10px'}),
                            html.Button("⏮ Reset", id="ecg-polar-reset",
                                        className="btn btn-secondary btn-sm",
                                        style={'width': '48%', 'marginTop': '10px'}),
                        ]),
                    ], id="ecg-polar-controls", style={'display': 'none', 'padding': '15px',
                                                       'backgroundColor': 'white', 'borderRadius': '8px',
                                                       'marginBottom': '20px',
                                                       'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                    # Phase Space Controls
                    html.Div([
                        html.H6("⚙️ Phase Space Controls",
                                style={'color': '#2c3e50', 'marginBottom': '10px'}),

                        html.Label("X-axis Lead:", style={'fontWeight': '600'}),
                        dcc.Dropdown(
                            id="ecg-phase-space-channel-1",
                            options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i}
                                     for i in range(min(num_leads, 12))],
                            value=DEFAULT_PHASE_SPACE_CHANNEL_1
                        ),

                        html.Label("Y-axis Lead:",
                                   style={'fontWeight': '600', 'marginTop': '10px'}),
                        dcc.Dropdown(
                            id="ecg-phase-space-channel-2",
                            options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i}
                                     for i in range(min(num_leads, 12))],
                            value=DEFAULT_PHASE_SPACE_CHANNEL_2
                        ),

                        html.Label(["Resolution: ",
                                    html.Span(id="ecg-phase-resolution-display",
                                              style={'color': '#3498db', 'fontWeight': 'bold'})],
                                   style={'marginTop': '10px'}),
                        dcc.Slider(id='ecg-phase-space-resolution',
                                   min=0.01, max=0.5, step=0.01, value=0.1,
                                   marks={0.05: '0.05', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),

                        html.Label("Colormap:",
                                   style={'fontWeight': '600', 'marginTop': '10px'}),
                        dcc.Dropdown(
                            id="ecg-colormap-select",
                            options=[{"label": cm, "value": cm} for cm in AVAILABLE_COLORMAPS],
                            value=DEFAULT_COLORMAP
                        ),
                    ], id="ecg-phase-space-controls", style={'display': 'none', 'padding': '15px',
                                                             'backgroundColor': 'white', 'borderRadius': '8px',
                                                             'marginBottom': '20px',
                                                             'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                    # === DIAGNOSIS BUTTON ===
                    html.Div([
                        html.Button("🔬 Diagnose",
                                    id="ecg-diagnose-btn",
                                    className="btn btn-primary btn-lg",
                                    style={'width': '100%'}),
                    ], style={
                        'padding': '15px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),

                ], style={
                    'overflowY': 'auto',
                    'height': '100vh',
                    'padding': '20px'
                })
            ], style={
                'width': '400px',
                'backgroundColor': '#e9ecef',
                'borderLeft': '2px solid #dee2e6',
                'overflowY': 'auto'
            }),

        ], style={
            'display': 'flex',
            'height': '100vh',
            'overflow': 'hidden'
        }),

        # Hidden components
        dcc.Interval(id='ecg-interval', interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id='ecg-continuous-playing', data=False),
        dcc.Store(id='ecg-polar-playing', data=False),
        dcc.Store(id='ecg-signal-length', data=0),
        dcc.Store(id='ecg-polar-cumulative-data', data=[]),
        dcc.Store(id='ecg-polar-position', data=0),
        html.Button("Pause", id="ecg-play-pause", style={"display": "none"}),
    ])