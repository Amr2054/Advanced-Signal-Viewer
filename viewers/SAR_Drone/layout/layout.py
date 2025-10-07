import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc


def SAR_app_layout():
    return dbc.Container([
    # Title
    dbc.Row([
        dbc.Col([
            html.H1("🌍 Disaster Detection System", className="text-center my-4"),
            html.Hr()
        ])
    ]),

    # Three Frames: SAR Earthquake, Audio, and SAR TIFF Analysis
    dbc.Row([
        # SAR Earthquake Detection frame
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("🛰️ SAR Earthquake Damage")),
                dbc.CardBody([
                    html.P("Upload Sentinel-1 SAR image (.npy format)"),
                    html.P("4 channels: [pre_VV, pre_VH, post_VV, post_VH]",
                           className="text-muted small"),

                    # SAR Upload
                    dcc.Upload(
                        id='upload-sar',
                        children=html.Div([
                            '🖼️ Drag & Drop or ',
                            html.A('Select SAR Image (.npy)')
                        ]),
                        style={
                            'width': '100%',
                            'height': '80px',
                            'lineHeight': '80px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'backgroundColor': '#f8f9fa'
                        },
                        accept='.npy'
                    ),
                    html.Div(id='sar-result', className="mt-3")
                ])
            ], className="shadow-sm")
        ], md=4),

        # Audio frame
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("🎵 Audio Classification")),
                dbc.CardBody([

                    html.P("Upload audio file for drone/bird detection"),
                    html.P("Supported formats: .wav, .mp3",
                           className="text-muted small"),

                    dcc.Upload(
                        id='upload-audio',
                        children=html.Div([
                            '🔊 Drag & Drop or ',
                            html.A('Select Audio File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '80px',
                            'lineHeight': '80px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'backgroundColor': '#f8f9fa'
                        },
                        accept='.wav,.mp3'
                    ),

                    #Audio player (hidden until a file is uploaded)
                    html.Div(id='audio-player-div', children=[]),

                    #Spectrogram graph (hidden until a file is uploaded)
                    dcc.Graph(
                        id='spectrogram-graph',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    ),
                    dcc.Interval(id='spectrogram-interval', interval=200, n_intervals=0),
                    dcc.Store(id='spectrogram-data'),
                    html.Div(id='audio-result', className="mt-3")
                ])
            ], className="shadow-sm")
        ], md=4),

        # SAR TIFF Analysis frame
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("📡 SAR Signal Analysis")),
                dbc.CardBody([

                    dcc.Upload(
                        id='upload-vv',
                        children=html.Div(['📄 Select VV TIFF']),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '5px 0',
                            'backgroundColor': '#f8f9fa',
                            'fontSize': '14px'
                        },
                        accept='.tif,.tiff'
                    ),
                    html.Div(id='vv-status', className="small text-muted"),

                    dcc.Upload(
                        id='upload-vh',
                        children=html.Div(['📄 Select VH TIFF (Optional)']),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '5px 0',
                            'backgroundColor': '#f8f9fa',
                            'fontSize': '14px'
                        },
                        accept='.tif,.tiff'
                    ),
                    html.Div(id='vh-status', className="small text-muted"),

                    dbc.Button("Analyze", id="analyze-tiff-btn", color="primary",
                               className="mt-2 w-100", size="sm", disabled=True),
                ])
            ], className="shadow-sm")
        ], md=4)

    ], className="mb-4"),

    # Results
    dbc.Row([
        dbc.Col([html.Div(id='tiff-result')])
    ]),

    # Hidden storage
    dcc.Store(id='vv-store'),
    dcc.Store(id='vh-store'),

], fluid=True)
