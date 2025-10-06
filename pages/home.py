from dash import html
import dash_bootstrap_components as dbc

# Define viewer cards with enhanced information
viewer_cards = [
    {
        "title": "ECG Viewer",
        "description": "Advanced electrocardiogram signal visualization with AI-powered diagnosis and multiple viewing modes.",
        "icon": "❤️",
        "features": [
            "Multi-lead ECG visualization",
            "AI-powered diagnosis",
            "XOR time chunks analysis",
            "Polar Coordinates analysis",
        ],
        "href": "/ecg-viewer",
        "color": "danger",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "available": True
    },
    {
        "title": "EEG Viewer",
        "description": "Comprehensive brain wave monitoring and analysis with AI-powered diagnosis.",
        "icon": "🧠",
        "features": [
            "Multi-channel EEG display",
            "AI-powered diagnosis",
            "Polar Coordinates analysis",
            "Event detection",
        ],
        "href": "/EEG-viewer",
        "color": "primary",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "available": True
    },
    {
        "title": "Doppler Viewer",
        "description": "Doppler signal generation & detection using AI.",
        "icon": "🌊",
        "features": [
            "Doppler waveform analysis",
            "Velocity measurements",
            "Sound Generation",
            "Doppler signal detection"
        ],
        "href": "/doppler-viewer",
        "color": "success",
        "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "available": True
    },
    {
        "title": "SAR - Drone Viewer",
        "description": "Earthquake & Drone Detection using AI.",
        "icon": "🚁",
        "features": [
            "Earthquake detection using SAR data",
            "Drone detection",
        ],
        "href": "/SAR-Drone",
        "color": "warning",
        "gradient": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "available": True
    }
]


def create_viewer_card(viewer):
    """
    Create an enhanced card component with hover effects and modern styling
    """
    features = html.Ul([
        html.Li([
            html.I(className="bi bi-check-circle-fill me-2", style={'color': '#28a745'}),
            feature
        ], className="mb-2", style={'fontSize': '14px', 'color': '#555'})
        for feature in viewer["features"]
    ], className="mb-3", style={'listStyle': 'none', 'paddingLeft': '0'})

    if viewer["available"]:
        button = dbc.Button(
            [html.I(className="bi bi-arrow-right-circle me-2"), "Launch Viewer"],
            href=viewer["href"],
            color=viewer["color"],
            className="w-100 btn-lg hover-button",
            style={
                'fontWeight': '600',
                'letterSpacing': '0.5px',
                'transition': 'all 0.3s'
            }
        )
    else:
        button = dbc.Button(
            "Coming Soon",
            color="secondary",
            disabled=True,
            className="w-100 btn-lg"
        )

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H2(viewer["icon"], className="text-center mb-3",
                        style={"fontSize": "5rem", "filter": "drop-shadow(0 4px 6px rgba(0,0,0,0.1))"}),
            ], style={
                'background': viewer["gradient"],
                'margin': '-1.25rem -1.25rem 1.5rem -1.25rem',
                'padding': '2rem',
                'borderRadius': '0.5rem 0.5rem 0 0'
            }),
            html.H4(viewer["title"], className="card-title text-center mb-3",
                    style={'fontWeight': '700', 'color': '#2c3e50'}),
            html.P(viewer["description"], className="card-text text-center mb-4",
                   style={'color': '#7f8c8d', 'fontSize': '15px', 'lineHeight': '1.6'}),
            html.Hr(style={'margin': '1.5rem 0'}),
            html.H6("Key Features", className="fw-bold mb-3", style={'color': '#34495e'}),
            features,
            button
        ])
    ], className="h-100 hover-card", style={
        'border': 'none',
        'borderRadius': '1rem',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.1)',
        'transition': 'all 0.3s ease',
        'overflow': 'hidden'
    })


# Main layout with enhanced styling
layout = html.Div([
    # Custom CSS - Create assets/custom.css file with this content instead
    html.Link(
        rel='stylesheet',
        href='/assets/custom.css'
    ),

    # Hero Section
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1(
                        "EchoSphere",
                        className="text-center fw-bold mb-4",
                        style={
                            'fontSize': '4rem',
                            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent',
                            'backgroundClip': 'text',
                            'textShadow': '0 2px 10px rgba(102, 126, 234, 0.3)'
                        }
                    ),
                    html.P(
                        "Professional tools for Signals analysis and visualization",
                        className="text-center lead mb-4",
                        style={
                            'fontSize': '1.4rem',
                            'color': '#7f8c8d',
                            'fontWeight': '400'
                        }
                    ),
                    html.Div([
                        html.Span("AI-Powered", className="badge bg-primary me-2 mb-2 p-2",
                                  style={'fontSize': '14px'}),
                        html.Span("Medical Signals", className="badge bg-success me-2 mb-2 p-2",
                                  style={'fontSize': '14px'}),
                        html.Span("Acoustic Signals", className="badge bg-info me-2 mb-2 p-2",
                                  style={'fontSize': '14px'}),
                        html.Span("Radio frequency Signals", className="badge bg-warning me-2 mb-2 p-2",
                                  style={'fontSize': '14px'}),
                    ], className="text-center mb-5")
                ], width=12)
            ])
        ])
    ], style={
        'background': 'linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%)',
        'padding': '4rem 0 3rem 0',
        'marginBottom': '3rem'
    }),

    # Viewer Cards Section
    dbc.Container([
        html.H2("Choose Your Viewer",
                className="text-center fw-bold mb-5",
                style={'color': '#2c3e50', 'fontSize': '2.5rem'}),

        dbc.Row([
            dbc.Col(
                create_viewer_card(viewer),
                width=12,
                md=6,
                lg=3,
                className="mb-4"
            )
            for viewer in viewer_cards
        ], className="mb-5 g-4"),
    ], fluid=False),

    # Features Section
    html.Div([
        dbc.Container([
            html.H2("Why Choose Our Platform?",
                    className="text-center fw-bold mb-5",
                    style={'color': 'white', 'fontSize': '2.5rem'}),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-lightning-charge-fill",
                               style={'fontSize': '3rem', 'color': '#ffd700'}),
                        html.H4("Fast & Responsive", className="mt-3 mb-2",
                                style={'color': 'white', 'fontWeight': '600'}),
                        html.P("Real-time signal processing with instant visualization updates",
                               style={'color': 'rgba(255,255,255,0.8)', 'fontSize': '15px'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-shield-check",
                               style={'fontSize': '3rem', 'color': '#4CAF50'}),
                        html.H4("Accurate & Reliable", className="mt-3 mb-2",
                                style={'color': 'white', 'fontWeight': '600'}),
                        html.P("AI-powered analysis with high precision diagnostic capabilities",
                               style={'color': 'rgba(255,255,255,0.8)', 'fontSize': '15px'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-bar-chart-line",
                               style={'fontSize': '3rem', 'color': '#2196F3'}),
                        html.H4("Advanced Analytics", className="mt-3 mb-2",
                                style={'color': 'white', 'fontWeight': '600'}),
                        html.P("Multiple visualization modes with comprehensive analysis tools",
                               style={'color': 'rgba(255,255,255,0.8)', 'fontSize': '15px'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-people-fill",
                               style={'fontSize': '3rem', 'color': '#FF5722'}),
                        html.H4("User Friendly", className="mt-3 mb-2",
                                style={'color': 'white', 'fontWeight': '600'}),
                        html.P("Intuitive interface designed for medical professionals",
                               style={'color': 'rgba(255,255,255,0.8)', 'fontSize': '15px'})
                    ], className="text-center p-4")
                ], md=3),
            ])
        ])
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '5rem 0',
        'marginTop': '4rem'
    }),

    # Quick Start Section
    dbc.Container([
        html.Div([
            html.H2("Getting Started",
                    className="text-center fw-bold mb-5 mt-5",
                    style={'color': '#2c3e50', 'fontSize': '2.5rem'}),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("1", className="step-number mb-3"),
                        html.H5("Select Viewer", className="mb-3", style={'fontWeight': '600'}),
                        html.P(
                            "Choose the appropriate signal viewer from the cards above based on your analysis needs.",
                            style={'color': '#7f8c8d'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.Div("2", className="step-number mb-3"),
                        html.H5("Load Signal", className="mb-3", style={'fontWeight': '600'}),
                        html.P("Select a signal record from the available dataset or upload your own data.",
                               style={'color': '#7f8c8d'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.Div("3", className="step-number mb-3"),
                        html.H5("Choose Mode", className="mb-3", style={'fontWeight': '600'}),
                        html.P("Select your preferred visualization mode from multiple available options.",
                               style={'color': '#7f8c8d'})
                    ], className="text-center p-4")
                ], md=3),

                dbc.Col([
                    html.Div([
                        html.Div("4", className="step-number mb-3"),
                        html.H5("Analyze", className="mb-3", style={'fontWeight': '600'}),
                        html.P("Use advanced tools to analyze, diagnose, and extract insights from signals.",
                               style={'color': '#7f8c8d'})
                    ], className="text-center p-4")
                ], md=3),
            ])
        ], className="mb-5")
    ], fluid=False),

], style={'backgroundColor': '#ffffff'})