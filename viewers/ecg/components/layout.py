"""
ECG Viewer Layout Components - FIXED VERSION
Clean UI with new features
"""
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


def create_ecg_layout(num_records, num_leads):
    """Create the ECG viewer layout"""

    return html.Div([
        html.H2("ECG Viewer"),

        # Record selection
        html.Label("Select ECG Record:"),
        dcc.Dropdown(
            id="ecg-record-select",
            options=[{"label": f"Record {i}", "value": i} for i in range(num_records)],
            value=0,
            clearable=False,
            className="mb-3"
        ),

        # Channel selection
        html.Label("Select Leads to Display:"),
        dcc.Checklist(
            id='ecg-channel-select',
            options=[{'label': f'Lead {i + 1}', 'value': i} for i in range(num_leads)],
            value=DEFAULT_SELECTED_CHANNELS,
            inline=True,
            className="mb-3"
        ),

        # View mode selection
        html.Label("Select View Mode:"),
        dcc.RadioItems(
            id='ecg-mode-select',
            options=[
                {'label': 'Static (10s)', 'value': 'static'},
                {'label': 'Continuous Viewer', 'value': 'continuous'},
                {'label': 'XOR Time Chunks', 'value': 'xor_chunks'},
                {'label': 'Polar Graph', 'value': 'polar_new'},
                {'label': 'Phase Space Recurrence', 'value': 'phase_space'},
            #    {'label': 'ICU Monitor', 'value': 'icu_monitor'},
            ],
            value='static',
            inline=True,
            className="mb-3"
        ),

        # Continuous Viewer Controls
        html.Div([
            html.H5("Continuous Viewer Controls"),
            html.Div([
                html.Button("⏮ Reset", id="ecg-continuous-reset", className="btn btn-secondary btn-sm me-1"),
                html.Button("◀ Pan Left", id="ecg-continuous-pan-left", className="btn btn-info btn-sm me-1"),
                html.Button("▶ Play", id="ecg-continuous-play-pause", className="btn btn-success btn-sm me-1"),
                html.Button("Pan Right ▶", id="ecg-continuous-pan-right", className="btn btn-info btn-sm"),
            ], className="mb-2"),
            html.Label(["Speed: ", html.Span(id="ecg-continuous-speed-display", className="text-primary")]),
            dcc.Slider(id='ecg-continuous-speed', min=CONTINUOUS_MIN_SPEED, max=CONTINUOUS_MAX_SPEED,
                      step=0.1, value=CONTINUOUS_DEFAULT_SPEED,
                      marks={0.1: '0.1x', 1.0: '1x', 2.0: '2x', 5.0: '5x'}),
            html.Label(["Zoom: ", html.Span(id="ecg-continuous-zoom-display", className="text-primary")]),
            dcc.Slider(id='ecg-continuous-zoom', min=CONTINUOUS_MIN_WINDOW, max=CONTINUOUS_MAX_WINDOW,
                      step=0.5, value=CONTINUOUS_DEFAULT_WINDOW,
                      marks={1: '1s', 10: '10s', 30: '30s'}),
            html.Label(["Position: ", html.Span(id="ecg-continuous-position-display", className="text-primary")]),
            dcc.Slider(id='ecg-continuous-position', min=0, max=100, step=0.1, value=0, marks={}),
        ], id="ecg-continuous-controls", style={"display": "none"}, className="mb-3"),

        # XOR Chunks Controls
        html.Div([
            html.H5("XOR Time Chunks Controls"),
            html.Label("Select Channel:"),
            dcc.Dropdown(
                id="ecg-xor-chunks-channel",
                options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                value=0,
                className="mb-2"
            ),
            html.Label(["Chunk Period: ", html.Span(id="ecg-xor-chunk-period-display", className="text-primary")]),
            dcc.Slider(id='ecg-xor-chunk-period', min=XOR_CHUNKS_MIN_PERIOD, max=XOR_CHUNKS_MAX_PERIOD,
                      step=0.1, value=XOR_CHUNKS_DEFAULT_PERIOD,
                      marks={0.2: '0.2s', 1: '1s', 3: '3s', 5: '5s'}),
            html.Label(["Total Duration: ", html.Span(id="ecg-xor-duration-display", className="text-primary")]),
            dcc.Slider(id='ecg-xor-duration', min=2, max=30, step=1, value=XOR_CHUNKS_DEFAULT_DURATION,
                      marks={5: '5s', 10: '10s', 20: '20s', 30: '30s'}),
            html.Label(["XOR Threshold: ", html.Span(id="ecg-xor-threshold-display", className="text-primary")]),
            dcc.Slider(id='ecg-xor-chunks-threshold', min=0.01, max=0.5, step=0.01, value=0.05,
                      marks={0.01: '0.01', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),
        ], id="ecg-xor-chunks-controls", style={"display": "none"}, className="mb-3"),

        # Polar Controls
        html.Div([
            html.H5("Polar Graph Controls"),
            html.Label("Select Channel:"),
            dcc.Dropdown(
                id="ecg-polar-channel",
                options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                value=0,
                className="mb-2"
            ),
            html.Label(["Window Size: ", html.Span(id="ecg-polar-window-display", className="text-primary")]),
            dcc.Slider(id='ecg-polar-window', min=POLAR_MIN_WINDOW, max=POLAR_MAX_WINDOW,
                      step=0.5, value=POLAR_DEFAULT_WINDOW,
                      marks={1: '1s', 5: '5s', 10: '10s', 20: '20s'}),
            html.Label("Display Mode:"),
            dcc.RadioItems(
                id='ecg-polar-mode',
                options=[
                    {'label': 'Latest (fading)', 'value': 'latest'},
                    {'label': 'Cumulative', 'value': 'cumulative'}
                ],
                value='latest',
                inline=True,
                className="mb-2"
            ),
            html.Button("▶ Play", id="ecg-polar-play-pause", className="btn btn-success btn-sm me-1"),
            html.Button("⏮ Reset", id="ecg-polar-reset", className="btn btn-secondary btn-sm"),
        ], id="ecg-polar-controls", style={"display": "none"}, className="mb-3"),

        # Phase Space Controls
        html.Div([
            html.H5("Phase Space Controls"),
            html.Label("X-axis Channel:"),
            dcc.Dropdown(
                id="ecg-phase-space-channel-1",
                options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                value=DEFAULT_PHASE_SPACE_CHANNEL_1,
                className="mb-2"
            ),
            html.Label("Y-axis Channel:"),
            dcc.Dropdown(
                id="ecg-phase-space-channel-2",
                options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                value=DEFAULT_PHASE_SPACE_CHANNEL_2,
                className="mb-2"
            ),
            html.Label(["Grid Resolution: ", html.Span(id="ecg-phase-resolution-display", className="text-primary")]),
            dcc.Slider(id='ecg-phase-space-resolution', min=0.01, max=0.5, step=0.01, value=0.1,
                      marks={0.05: '0.05', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'}),
            html.Label("Colormap:"),
            dcc.Dropdown(
                id="ecg-colormap-select",
                options=[{"label": cm, "value": cm} for cm in AVAILABLE_COLORMAPS],
                value=DEFAULT_COLORMAP,
                className="mb-2"
            ),
        ], id="ecg-phase-space-controls", style={"display": "none"}, className="mb-3"),

        # Action buttons
        html.Div([
            html.Button("Diagnose", id="ecg-diagnose-btn", className="btn btn-primary me-2"),
            html.Button("Pause", id="ecg-play-pause", style={"display": "none"}, className="btn btn-warning"),
        ], className="mb-3"),

        # Output displays
        html.Div(id="ecg-bpm-output", className="alert alert-success", style={"marginTop": "20px"}),
        dcc.Graph(id='ecg-graph', config={'displayModeBar': True}),
        html.Div(id="ecg-diagnosis-output", className="alert alert-info", style={"marginTop": "20px"}),

        # Hidden components
        dcc.Interval(id='ecg-interval', interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id='ecg-continuous-playing', data=False),
        dcc.Store(id='ecg-polar-playing', data=False),
        dcc.Store(id='ecg-signal-length', data=0),
        dcc.Store(id='ecg-polar-cumulative-data', data=[]),
    ])