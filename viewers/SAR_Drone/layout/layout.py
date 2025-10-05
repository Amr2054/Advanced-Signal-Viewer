from dash import dcc, html, Input, Output, State
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

        # Two Frames: SAR and Audio
        dbc.Row([

            # SAR frame
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3("🛰️ SAR Image Analysis")),
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

                        # SAR Result
                        html.Div(id='sar-result', className="mt-3")
                    ])
                ], className="shadow-sm")
            ], md=6),

            # Audio frame
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3("🎵 Audio Classification")),
                    dbc.CardBody([
                        html.P("Upload audio file for drone/bird detection"),
                        html.P("Supported formats: .wav, .mp3",
                               className="text-muted small"),

                        # Audio Upload
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

                        # Audio Result
                        html.Div(id='audio-result', className="mt-3")
                    ])
                ], className="shadow-sm")
            ], md=6)

        ], className="mb-4"),

        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P("Powered by PyTorch + Dash",
                       className="text-center text-muted")
            ])
        ])

    ], fluid=True)