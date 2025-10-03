# """
# Dash layout components
# """
# from dash import dcc, html
# from config import (
#     DEFAULT_SELECTED_CHANNELS,
#     DEFAULT_XOR_CHANNEL_1,
#     DEFAULT_XOR_CHANNEL_2,
#     DEFAULT_PHASE_SPACE_CHANNEL_1,
#     DEFAULT_PHASE_SPACE_CHANNEL_2
# )
#
#
# def create_layout(num_records, num_leads):
#     """
#     Create the main application layout
#
#     Args:
#         num_records (int): Total number of ECG records
#         num_leads (int): Number of leads per record
#
#     Returns:
#         html.Div: Dash layout component
#     """
#     return html.Div([
#         html.H2("ECG Viewer"),
#
#         # Record selection
#         html.Label("Select ECG Record:"),
#         dcc.Dropdown(
#             id="record-select",
#             options=[{"label": f"Record {i}", "value": i} for i in range(num_records)],
#             value=0,
#             clearable=False
#         ),
#
#         # Channel selection
#         dcc.Checklist(
#             id='channel-select',
#             options=[{'label': f'Lead {i + 1}', 'value': i} for i in range(num_leads)],
#             value=DEFAULT_SELECTED_CHANNELS,
#             inline=True
#         ),
#
#         # XOR mode options (hidden by default)
#         html.Div([
#             html.Label("Select Channel 1 for XOR:"),
#             dcc.Dropdown(
#                 id="xor-channel-1",
#                 options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
#                 value=DEFAULT_XOR_CHANNEL_1,
#             ),
#             html.Label("Select Channel 2 for XOR:"),
#             dcc.Dropdown(
#                 id="xor-channel-2",
#                 options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
#                 value=DEFAULT_XOR_CHANNEL_2,
#             ),
#             html.Label("XOR Threshold (mV):"),
#             dcc.Slider(
#                 id='xor-threshold',
#                 min=0.01,
#                 max=0.5,
#                 step=0.01,
#                 value=0.05,
#                 marks={i/100: str(i/100) for i in range(1, 51, 10)},
#                 tooltip={"placement": "bottom", "always_visible": True}
#             ),
#         ], id="xor-options", style={"display": "none"}),
#
#         # Phase Space options (hidden by default)
#         html.Div([
#             html.Label("Select Channel for X-axis:"),
#             dcc.Dropdown(
#                 id="phase-space-channel-1",
#                 options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
#                 value=DEFAULT_PHASE_SPACE_CHANNEL_1,
#             ),
#             html.Label("Select Channel for Y-axis:"),
#             dcc.Dropdown(
#                 id="phase-space-channel-2",
#                 options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
#                 value=DEFAULT_PHASE_SPACE_CHANNEL_2,
#             ),
#             html.Label("Grid Resolution (mV):"),
#             dcc.Slider(
#                 id='phase-space-resolution',
#                 min=0.01,
#                 max=0.5,
#                 step=0.01,
#                 value=0.1,
#                 marks={i/100: str(i/100) for i in range(5, 51, 10)},
#                 tooltip={"placement": "bottom", "always_visible": True}
#             ),
#         ], id="phase-space-options", style={"display": "none"}),
#
#         # View mode selection
#         html.Label("Select View Mode:"),
#         dcc.RadioItems(
#             id='mode-select',
#             options=[
#                 {'label': 'Static (10s)', 'value': 'static'},
#                 {'label': 'ICU Monitor (Live)', 'value': 'icu_monitor'},
#              #   {'label': 'Dynamic (heartbeat)', 'value': 'dynamic'},
#                 {'label': 'Polar (heartbeat)', 'value': 'polar'},
#                 {'label': 'XOR Comparison (5s)', 'value': 'xor_mode'},
#                 {'label': 'Phase Space Recurrence (10s)', 'value': 'phase_space'}
#             ],
#             value='static',
#             inline=True
#         ),
#
#         # Control buttons
#         html.Button("Pause", id="play-pause", n_clicks=0, style={"display": "none"}),
#         html.Button("Diagnose", id="diagnose-btn", n_clicks=0),
#
#         # Output displays
#         html.Div(
#             id="bpm-output",
#             style={"marginTop": "20px", "fontSize": "18px", "color": "green"}
#         ),
#         dcc.Graph(id='ecg-graph'),
#         html.Div(
#             id="diagnosis-output",
#             style={"marginTop": "20px", "fontSize": "20px", "color": "blue"}
#         ),
#
#         # Interval component for animation
#         dcc.Interval(id='interval', interval=1000, n_intervals=0, disabled=True)
#     ])

from dash import dcc, html
from config import (
    DEFAULT_SELECTED_CHANNELS,
    DEFAULT_XOR_CHANNEL_1,
    DEFAULT_XOR_CHANNEL_2,
    DEFAULT_PHASE_SPACE_CHANNEL_1,
    DEFAULT_PHASE_SPACE_CHANNEL_2
)

def create_layout(num_records, num_leads):
    """
    Create the main application layout with enhanced styling and wider layout

    Args:
        num_records (int): Total number of ECG records
        num_leads (int): Number of leads per record

    Returns:
        html.Div: Dash layout component with Tailwind CSS styling
    """
    return html.Div([
        # Include Tailwind CSS CDN
        html.Link(
            rel='stylesheet',
            href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'
        ),

        # Main container with increased width
        html.Div([
            html.H2(
                "ECG Viewer",
                className="text-3xl font-bold text-gray-800 mb-6 text-center"
            ),

            # Record selection
            html.Label(
                "Select ECG Record:",
                className="block text-lg font-medium text-gray-700 mb-2"
            ),
            dcc.Dropdown(
                id="record-select",
                options=[{"label": f"Record {i}", "value": i} for i in range(num_records)],
                value=0,
                clearable=False,
                className="w-full border border-gray-300 rounded-md p-2 mb-4"
            ),

            # Channel selection
            html.Label(
                "Select Channels:",
                className="block text-lg font-medium text-gray-700 mb-2"
            ),
            dcc.Checklist(
                id='channel-select',
                options=[{'label': f'Lead {i + 1}', 'value': i} for i in range(num_leads)],
                value=DEFAULT_SELECTED_CHANNELS,
                inline=True,
                className="flex flex-wrap gap-4 mb-4"
            ),

            # XOR mode options (hidden by default)
            html.Div([
                html.Label(
                    "Select Channel 1 for XOR:",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Dropdown(
                    id="xor-channel-1",
                    options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                    value=DEFAULT_XOR_CHANNEL_1,
                    className="w-full border border-gray-300 rounded-md p-2 mb-4"
                ),
                html.Label(
                    "Select Channel 2 for XOR:",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Dropdown(
                    id="xor-channel-2",
                    options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                    value=DEFAULT_XOR_CHANNEL_2,
                    className="w-full border border-gray-300 rounded-md p-2 mb-4"
                ),
                html.Label(
                    "XOR Threshold (mV):",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Slider(
                    id='xor-threshold',
                    min=0.01,
                    max=0.5,
                    step=0.01,
                    value=0.05,
                    marks={i/100: str(i/100) for i in range(1, 51, 10)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="w-full mb-4"
                ),
            ], id="xor-options", className="bg-gray-50 p-4 rounded-md mb-4", style={"display": "none"}),

            # Phase Space options (hidden by default)
            html.Div([
                html.Label(
                    "Select Channel for X-axis:",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Dropdown(
                    id="phase-space-channel-1",
                    options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                    value=DEFAULT_PHASE_SPACE_CHANNEL_1,
                    className="w-full border border-gray-300 rounded-md p-2 mb-4"
                ),
                html.Label(
                    "Select Channel for Y-axis:",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Dropdown(
                    id="phase-space-channel-2",
                    options=[{"label": f"Lead {i + 1}", "value": i} for i in range(num_leads)],
                    value=DEFAULT_PHASE_SPACE_CHANNEL_2,
                    className="w-full border border-gray-300 rounded-md p-2 mb-4"
                ),
                html.Label(
                    "Grid Resolution (mV):",
                    className="block text-lg font-medium text-gray-700 mb-2"
                ),
                dcc.Slider(
                    id='phase-space-resolution',
                    min=0.01,
                    max=0.5,
                    step=0.01,
                    value=0.1,
                    marks={i/100: str(i/100) for i in range(5, 51, 10)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="w-full mb-4"
                ),
            ], id="phase-space-options", className="bg-gray-50 p-4 rounded-md mb-4", style={"display": "none"}),

            # View mode selection with enhanced radio items
            html.Label(
                "Select View Mode:",
                className="block text-lg font-medium text-gray-700 mb-2"
            ),
            dcc.RadioItems(
                id='mode-select',
                options=[
                    {'label': 'Static (10s)', 'value': 'static'},
                    {'label': 'ICU Monitor (Live)', 'value': 'icu_monitor'},
                    {'label': 'Polar (heartbeat)', 'value': 'polar'},
                    {'label': 'XOR Comparison (5s)', 'value': 'xor_mode'},
                    {'label': 'Phase Space Recurrence (10s)', 'value': 'phase_space'}
                ],
                value='static',
                className="flex flex-wrap gap-4 mb-4",
                inputClassName="mr-2",
                labelClassName="text-gray-700 hover:text-blue-600 cursor-pointer"
            ),

            # Control buttons
            html.Div([
                html.Button(
                    "Pause",
                    id="play-pause",
                    n_clicks=0,
                    className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 mr-2",
                    style={"display": "none"}
                ),
                html.Button(
                    "Diagnose",
                    id="diagnose-btn",
                    n_clicks=0,
                    className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
                ),
            ], className="flex gap-2 mb-4"),

            # Output displays
            html.Div(
                id="bpm-output",
                className="text-lg text-green-600 mt-5 mb-4"
            ),
            dcc.Graph(
                id='ecg-graph',
                className="border border-gray-200 rounded-md"
            ),
            html.Div(
                id="diagnosis-output",
                className="text-xl text-blue-600 mt-5"
            ),

            # Interval component for animation
            dcc.Interval(id='interval', interval=1000, n_intervals=0, disabled=True)
        ], className="max-w-10xl mx-auto p-6 bg-white shadow-md rounded-md")
    ])