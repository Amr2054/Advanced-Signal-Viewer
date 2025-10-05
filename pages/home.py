"""
Home Page Layout
Landing page with navigation to different signal viewers
"""
from dash import html
import dash_bootstrap_components as dbc

# Define viewer cards
viewer_cards = [
    {
        "title": "ECG Viewer",
        "description": "Electrocardiogram signal visualization and analysis. View cardiac signals in multiple modes including ICU monitor, polar plots, and phase space analysis.",
        "icon": "❤️",
        "features": [
            "Multi-lead ECG visualization",
            "Real-time ICU monitor simulation",
            "Heart rate detection and BPM calculation",
            "AI-powered diagnosis (NORM, MI, STTC, CD, HYP)",
            "XOR comparison mode",
            "Phase space recurrence plots"
        ],
        "href": "/ecg-viewer",
        "color": "danger",
        "available": True
    },
    {
        "title": "EEG Viewer",
        "description": "Electroencephalogram signal visualization and analysis. Brain wave monitoring and analysis tools.",
        "icon": "🧠",
        "features": [
            "Multi-channel EEG display",
            "Frequency band analysis",
            "Spectral analysis",
            "Event detection",
            "Artifact removal"
        ],
        "href": "/EEG-viewer",
        "color": "primary",
        "available": True  # Coming soon
    },
    {
        "title": "Doppler Viewer",
        "description": "Universal signal viewer for custom physiological signals. Import and analyze any time-series data.",
        "icon": "📊",
        "features": [
            "Custom signal import",
            "Multi-channel support",
            "Time-frequency analysis",
            "Signal filtering",
            "Export capabilities"
        ],
        "href": "/doppler-viewer",
        "color": "success",
        "available": True  # Coming soon
    },
    {
        "title": "SAR - Drone Viewer",
        "description": "Universal signal viewer for custom physiological signals. Import and analyze any time-series data.",
        "icon": "📊",
        "features": [
            "Custom signal import",
            "Multi-channel support",
            "Time-frequency analysis",
            "Signal filtering",
            "Export capabilities"
        ],
        "href": "/SAR-Drone",
        "color": "success",
        "available": True  # Coming soon
    }
]


def create_viewer_card(viewer):
    """
    Create a card component for a signal viewer

    Args:
        viewer (dict): Viewer information

    Returns:
        dbc.Card: Bootstrap card component
    """
    # Feature list
    features = html.Ul([
        html.Li(feature, className="text-muted small")
        for feature in viewer["features"]
    ], className="mb-3")

    # Button
    if viewer["available"]:
        button = dbc.Button(
            "Launch Viewer",
            href=viewer["href"],
            color=viewer["color"],
            className="w-100"
        )
    else:
        button = dbc.Button(
            "Coming Soon",
            color="secondary",
            disabled=True,
            className="w-100"
        )

    # Card
    return dbc.Card([
        dbc.CardBody([
            html.H2(viewer["icon"], className="text-center mb-3", style={"fontSize": "4rem"}),
            html.H4(viewer["title"], className="card-title text-center"),
            html.P(viewer["description"], className="card-text text-muted mb-3"),
            html.Hr(),
            html.H6("Features:", className="fw-bold"),
            features,
            button
        ])
    ], className="shadow-sm h-100")


# Main layout
layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1(
                "Advanced Signal Viewer",
                className="text-center display-3 fw-bold mt-5 mb-3"
            ),
            html.P(
                "Professional tools for physiological signal analysis and visualization",
                className="text-center text-muted lead mb-5"
            ),
        ], width=12)
    ]),

    # Viewer cards
    dbc.Row([
        dbc.Col(
            create_viewer_card(viewer),
            width=12,
            md=6,
            lg=4,
            className="mb-4"
        )
        for viewer in viewer_cards
    ], className="mb-5"),

    # Info section
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.H4("About This Application", className="mt-4"),
            html.P([
                "This is a comprehensive signal viewing platform designed for medical and research professionals. ",
                "Each viewer provides specialized tools for analyzing different types of physiological signals. ",
                "Select a viewer above to get started."
            ], className="text-muted"),

            html.H4("Quick Start", className="mt-4"),
            html.Ol([
                html.Li("Choose a signal viewer from the cards above"),
                html.Li("Select a signal record to analyze"),
                html.Li("Choose your preferred visualization mode"),
                html.Li("Explore different analysis tools and features")
            ], className="text-muted"),

            html.H4("Technical Information", className="mt-4"),
            html.P([
                "Built with Dash and Plotly for interactive, real-time signal visualization. ",
                "Supports multiple viewing modes, AI-powered analysis, and advanced signal processing algorithms."
            ], className="text-muted mb-5"),
        ], width=12)
    ])

], fluid=False, className="px-4")