from dash import dcc, html
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
    'I',      # Lead I (Limb lead)
    'II',     # Lead II (Limb lead)
    'III',    # Lead III (Limb lead)
    'aVR',    # Augmented Vector Right
    'aVL',    # Augmented Vector Left
    'aVF',    # Augmented Vector Foot
    'V1',     # Precordial lead V1
    'V2',     # Precordial lead V2
    'V3',     # Precordial lead V3
    'V4',     # Precordial lead V4
    'V5',     # Precordial lead V5
    'V6',     # Precordial lead V6
]

def create_ecg_layout(num_records, num_leads):
    """Create compact ECG viewer layout with enhanced UI"""

    return html.Div([
        # Header
        html.H1("ECG Signal Viewer", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'}),

        # Record selection
        html.Div([
            html.Label("Select ECG Record:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Dropdown(
                id="ecg-record-select",
                options=[{"label": f"Record {i}", "value": i} for i in range(num_records)],
                value=None,
                clearable=False,
                style={'width': '100%'}
            ),
        ], style={'marginBottom': '25px'}),

        # Two-column layout for Leads and Mode
        html.Div([
            # Left Column - Lead Selection
            html.Div([
                html.Div([
                    html.Label("📡 Select Leads", style={
                        'fontWeight': 'bold',
                        'fontSize': '15px',
                        'marginBottom': '12px',
                        'display': 'block',
                        'color': '#34495e'
                    }),
                    html.Div([
                        html.Label([
                            dcc.Checklist(
                                id='ecg-channel-select',
                                # options=[{'label': f' Lead {i + 1}', 'value': i} for i in range(num_leads)],
                                options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i} for i in
                                         range(min(num_leads, 12))]
                                ,
                                value=DEFAULT_SELECTED_CHANNELS,
                                labelStyle={
                                    'display': 'inline-block',
                                    'margin': '5px 8px',
                                    'padding': '6px 12px',
                                    'border': '2px solid #3498db',
                                    'borderRadius': '6px',
                                    'cursor': 'pointer',
                                    'backgroundColor': '#ecf0f1',
                                    'transition': 'all 0.2s',
                                    'fontSize': '13px',
                                    'fontWeight': '500'
                                },

                                inputStyle={
                                    'marginRight': '6px',
                                    'transform': 'scale(1.1)'
                                }
                            )
                        ])
                    ], style={
                        'padding': '15px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '8px',
                        'border': '1px solid #dee2e6',
                        'maxHeight': '380px',
                        'overflowY': 'auto'
                    })
                ], style={
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'height': '100%'
                })
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),


            # Right Column - View Mode Selection
            html.Div([
                html.Div([
                    html.Label("🎨 Visualization Mode", style={
                        'fontWeight': 'bold',
                        'fontSize': '15px',
                        'marginBottom': '12px',
                        'display': 'block',
                        'color': '#34495e'
                    }),
                    html.Div([
                        dcc.RadioItems(
                            id='ecg-mode-select',
                            options=[
                                {'label': ' 📊 Static', 'value': 'static'},
                                {'label': ' 🎬 Continuous', 'value': 'continuous'},
                                {'label': ' ⚡ XOR Chunks', 'value': 'xor_chunks'},
                                {'label': ' 🌀 Polar', 'value': 'polar_new'},
                                {'label': ' 🎯 Phase Space', 'value': 'phase_space'},
                             #   {'label': ' 🏥 ICU Monitor', 'value': 'icu_monitor'},
                            ],
                            value='static',
                            labelStyle={
                                'display': 'block',
                                'padding': '10px 14px',
                                'margin': '6px 0',
                                'border': '2px solid #e0e0e0',
                                'borderRadius': '8px',
                                'cursor': 'pointer',
                                'transition': 'all 0.2s',
                                'backgroundColor': '#f8f9fa',
                                'fontSize': '13px',
                                'fontWeight': '500'
                            },
                            inputStyle={
                                'marginRight': '10px',
                                'transform': 'scale(1.15)'
                            }
                        )
                    ], style={
                        'padding': '10px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '8px',
                        'border': '1px solid #dee2e6',
                        'maxHeight': '380px',
                        'overflowY': 'auto'
                    })
                ], style={
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                    'height': '100%'
                })
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'}),

        ], style={'marginBottom': '25px'}),

        html.Div(id="ecg-bpm-output", className="alert alert-success",
                 style={"marginTop": "0px", "fontSize": "16px"}),
        html.Div(id="ecg-diagnosis-output", className="alert alert-info",
                 style={"marginTop": "0px", "fontSize": "16px"}),

        # Mode-specific controls (full width)
        html.Div([
            # Continuous Viewer Controls
            html.Div([
                html.Div([
                    html.H5("🎮 Continuous Viewer Controls", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.Div([
                        html.Button("⏮ Reset", id="ecg-continuous-reset", className="btn btn-secondary btn-sm me-1"),
                        html.Button("◀ Pan Left", id="ecg-continuous-pan-left", className="btn btn-info btn-sm me-1"),
                        html.Button("▶ Play", id="ecg-continuous-play-pause", className="btn btn-success btn-sm me-1"),
                        html.Button("Pan Right ▶", id="ecg-continuous-pan-right", className="btn btn-info btn-sm"),
                    ], style={'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.Label(["Speed: ", html.Span(id="ecg-continuous-speed-display",
                                                             style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-continuous-speed', min=CONTINUOUS_MIN_SPEED, max=CONTINUOUS_MAX_SPEED,
                                       step=0.1, value=CONTINUOUS_DEFAULT_SPEED,
                                       marks={0.1: '0.1x', 1.0: '1x', 2.0: '2x', 5.0: '5x'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Zoom: ", html.Span(id="ecg-continuous-zoom-display",
                                                            style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-continuous-zoom', min=CONTINUOUS_MIN_WINDOW, max=CONTINUOUS_MAX_WINDOW,
                                       step=0.5, value=CONTINUOUS_DEFAULT_WINDOW,
                                       marks={1: '1s', 10: '10s', 30: '30s'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Position: ", html.Span(id="ecg-continuous-position-display",
                                                                style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-continuous-position', min=0, max=100, step=0.1, value=0, marks={}),
                        ], style={'width': '32%', 'display': 'inline-block'}),
                    ])
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
            ], id="ecg-continuous-controls", style={"display": "none"}, className="mb-3"),

            # XOR Chunks Controls
            html.Div([
                html.Div([
                    html.H5("⚡ XOR Time Chunks Controls", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.Label("Channel:", style={'fontWeight': '600'}),
                            dcc.Dropdown(
                                id="ecg-xor-chunks-channel",
                                # options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                                options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i} for i in
                                         range(min(num_leads, 12))],
                                value=0
                            ),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Chunk Period: ", html.Span(id="ecg-xor-chunk-period-display",
                                                                    style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-xor-chunk-period', min=XOR_CHUNKS_MIN_PERIOD, max=XOR_CHUNKS_MAX_PERIOD,
                                       step=0.1, value=XOR_CHUNKS_DEFAULT_PERIOD,
                                       marks={0.2: '0.2s', 1: '1s', 3: '3s', 5: '5s'}),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Duration: ", html.Span(id="ecg-xor-duration-display",
                                                                style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-xor-duration', min=2, max=30, step=1, value=XOR_CHUNKS_DEFAULT_DURATION,
                                       marks={5: '5s', 10: '10s', 20: '20s', 30: '30s'}),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Threshold: ", html.Span(id="ecg-xor-threshold-display",
                                                                 style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-xor-chunks-threshold', min=0.01, max=0.5, step=0.01, value=0.05,
                                       marks={0.01: '0.01', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),
                        ], style={'width': '23%', 'display': 'inline-block'}),
                    ])
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
            ], id="ecg-xor-chunks-controls", style={"display": "none"}, className="mb-3"),

            # Polar Controls
            html.Div([
                html.Div([
                    html.H5("🌀 Polar Graph Controls", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.Label("Channel:", style={'fontWeight': '600'}),
                            dcc.Dropdown(
                                id="ecg-polar-channel",
                                # options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                                options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i} for i in
                                         range(min(num_leads, 12))],
                                value=0
                            ),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Window: ", html.Span(id="ecg-polar-window-display",
                                                              style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-polar-window', min=POLAR_MIN_WINDOW, max=POLAR_MAX_WINDOW,
                                       step=0.5, value=POLAR_DEFAULT_WINDOW,
                                       marks={1: '1s', 5: '5s', 10: '10s', 20: '20s'}),
                        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label("Display Mode:", style={'fontWeight': '600'}),
                            dcc.RadioItems(
                                id='ecg-polar-mode',
                                options=[
                                    {'label': ' Latest', 'value': 'latest'},
                                    {'label': ' Cumulative', 'value': 'cumulative'}
                                ],
                                value='latest',
                                inline=True
                            ),
                        ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%', 'paddingTop': '5px'}),
                        html.Div([
                            html.Button("▶ Play", id="ecg-polar-play-pause", className="btn btn-success btn-sm me-1"),
                            html.Button("⏮ Reset", id="ecg-polar-reset", className="btn btn-secondary btn-sm"),
                        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'right'}),
                    ])
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
            ], id="ecg-polar-controls", style={"display": "none"}, className="mb-3"),

            # Phase Space Controls
            html.Div([
                html.Div([
                    html.H5("🎯 Phase Space Controls", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.Label("X-axis Lead:", style={'fontWeight': '600'}),
                            dcc.Dropdown(
                                id="ecg-phase-space-channel-1",
                                # options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                                options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i} for i in
                                         range(min(num_leads, 12))],
                                value=DEFAULT_PHASE_SPACE_CHANNEL_1
                            ),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label("Y-axis Lead:", style={'fontWeight': '600'}),
                            dcc.Dropdown(
                                id="ecg-phase-space-channel-2",
                                # options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                                options=[{'label': f'Lead {ECG_LEAD_NAMES[i]}', 'value': i} for i in
                                         range(min(num_leads, 12))],
                                value=DEFAULT_PHASE_SPACE_CHANNEL_2
                            ),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label(["Resolution: ", html.Span(id="ecg-phase-resolution-display",
                                                                  style={'color': '#3498db', 'fontWeight': 'bold'})]),
                            dcc.Slider(id='ecg-phase-space-resolution', min=0.01, max=0.5, step=0.01, value=0.1,
                                       marks={0.05: '0.05', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),
                        ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
                        html.Div([
                            html.Label("Colormap:", style={'fontWeight': '600'}),
                            dcc.Dropdown(
                                id="ecg-colormap-select",
                                options=[{"label": cm, "value": cm} for cm in AVAILABLE_COLORMAPS],
                                value=DEFAULT_COLORMAP
                            ),
                        ], style={'width': '23%', 'display': 'inline-block'}),
                    ])
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
            ], id="ecg-phase-space-controls", style={"display": "none"}, className="mb-3"),
        ]),

        # Action buttons
        html.Div([
            html.Button("🔬 Diagnose", id="ecg-diagnose-btn", className="btn btn-primary btn-lg me-2"),
            html.Button("Pause", id="ecg-play-pause", style={"display": "none"}, className="btn btn-warning btn-lg"),
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),

        # Output displays

        dcc.Graph(id='ecg-graph', config={'displayModeBar': True}, style={'marginTop': '20px'}),


        # Hidden components
        dcc.Interval(id='ecg-interval', interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id='ecg-continuous-playing', data=False),
        dcc.Store(id='ecg-polar-playing', data=False),
        dcc.Store(id='ecg-signal-length', data=0),
        dcc.Store(id='ecg-polar-cumulative-data', data=[]),
        dcc.Store(id='ecg-polar-position', data=0),
    ])