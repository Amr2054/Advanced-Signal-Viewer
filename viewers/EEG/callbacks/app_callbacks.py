import dash
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from dash import html
from dash.dependencies import Input, Output, State
import base64
import tempfile
import zipfile
from dash.exceptions import PreventUpdate
from viewers.EEG.Data_helper import *
from viewers.EEG.visualize_utils import *
from viewers.EEG.layout.app_layout import *


# -----------------------
# Callbacks
# -----------------------
def app_callbacks(app):
    @app.callback(
        [Output('output-message', 'children'),
         Output('data-loaded', 'data'),
         Output('signal-duration', 'data'),
         Output('segment-dropdown', 'options'),
         Output('segment-dropdown', 'value')],
        [Input('upload-data', 'contents'),
         Input('upload-data', 'filename')]
    )
    def process_uploaded_files(contents, filename):
        global data_manager, plot_generator

        if contents is None:
            return html.Div("No files uploaded yet.", style={'color': '#7f8c8d'}), False, 0, [], None

        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, filename)
            with open(zip_path, 'wb') as f:
                f.write(decoded)

            with zipfile.ZipFile(zip_path, 'r') as archive:
                archive.extractall(tmpdir)
                extracted_files = archive.namelist()

                edf_file = None

                for f in extracted_files:
                    if f.endswith(".edf"):
                        edf_file = os.path.join(tmpdir, f)

                if edf_file is None:
                    return html.Div("No EDF file found in the archive.",
                                    style={'color': '#e74c3c'}), False, [], [], None

                # Initialize global instances
                data_manager = DataManager(edf_file)
                plot_generator = PlotGenerator(data_manager)

                # Calculate signal duration
                signal_duration = data_manager.total_samples / data_manager.original_sfreq

                # Create segment dropdown options
                segment_options = [
                    {
                        'label': f"Segment {i} ({s['start_time']:.1f}-{s['end_time']:.1f}s) - {'SEIZURE' if data_manager.segment_predictions[i]['is_seizure'] else 'Normal'}",
                        'value': i
                    }
                    for i, s in enumerate(data_manager.segments)
                ]

                # Count seizures
                seizure_count = sum(1 for p in data_manager.segment_predictions if p['is_seizure'])

                return html.Div([
                    html.P(f"✅ EDF file processed: {os.path.basename(edf_file)}", style={'color': '#27ae60'}),
                    html.P(f"📊 Total segments: {data_manager.n_segments}", style={'color': '#3498db'}),
                    html.P(f"⏱️ Signal duration: {signal_duration:.1f} seconds", style={'color': '#3498db'}),
                    html.P(f"⚠️ Seizures detected: {seizure_count}/{data_manager.n_segments}",
                           style={'color': '#e74c3c' if seizure_count > 0 else '#27ae60'})
                ]), True, signal_duration, segment_options, 0

    @app.callback(
        Output("summary-plot", "figure"),
        Input("data-loaded", "data")
    )
    def update_summary(data_loaded):
        global plot_generator

        if data_loaded and plot_generator:
            return plot_generator.create_summary_plot()
        return {}

    @app.callback(
        [Output('interval-component', 'disabled'),
         Output('playback-state', 'data')],
        [Input('play-button', 'n_clicks'),
         Input('stop-button', 'n_clicks')],
        [State('playback-state', 'data'),
         State('window-start', 'value')]
    )
    def control_playback(play_clicks, stop_clicks, state, window_start):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True, state

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'play-button':
            state['playing'] = True
            state['current_time'] = window_start
            return False, state
        elif button_id == 'stop-button':
            state['playing'] = False
            return True, state

        return True, state

    @app.callback(
        Output('window-start', 'value'),
        [Input('interval-component', 'n_intervals')],
        [State('playback-state', 'data'),
         State('window-start', 'value'),
         State('window-length', 'value'),
         State('playback-speed', 'value'),
         State('signal-duration', 'data')]
    )
    def update_playback_position(n, state, current_start, window_length, speed, duration):
        if not state['playing'] or n is None:
            raise PreventUpdate

        # Move window forward based on playback speed
        new_start = current_start + speed

        # Loop back to beginning if we reach the end
        if new_start + window_length > duration:
            new_start = 0

        return new_start

    @app.callback(
        Output("continuous-viewer", "figure"),
        [Input("continuous-channel", "value"),
         Input("window-start", "value"),
         Input("window-length", "value"),
         Input("data-loaded", "data")]
    )
    def update_continuous_viewer(channel_idx, window_start, window_length, data_loaded):
        global plot_generator

        if data_loaded and plot_generator:
            return plot_generator.create_continuous_viewer(channel_idx, window_start, window_length)
        return {}

    @app.callback(
        Output("segment-plots", "figure"),
        [Input("segment-dropdown", "value"),
         Input("channel-dropdown", "value"),
         Input("data-loaded", "data")]
    )
    def update_segment_plots(segment_idx, channel_idx, data_loaded):
        global plot_generator

        if data_loaded and plot_generator and segment_idx is not None:
            return plot_generator.create_segment_plots(segment_idx, channel_idx)
        return {}

    @app.callback(
        Output("crp-plot", "figure"),
        [Input("channel-1-dropdown", "value"),
         Input("channel-2-dropdown", "value"),
         Input("data-loaded", "data"),
         Input("ecg-colormap-select", "value")]
    )
    def update_crp(ch1_idx, ch2_idx, data_loaded,color):
        global plot_generator

        if data_loaded and plot_generator:
            return plot_generator.create_crp_plot(ch1_idx, ch2_idx,color)
        return {}
    
    @app.callback(
    Output("xor-graph", "figure"),
    [Input("xor-channel", "value"),
    Input("chunk-width", "value"),
    Input("Time","value"),
    Input("threshold","value"),
    Input("data-loaded", "data")]
    )
    def update_xor_graph(channel_idx, chunk_width, Time, threshold, data_loaded):
        global plot_generator
        
        if data_loaded and plot_generator and chunk_width:
            return plot_generator.create_xor_graph(channel_idx, chunk_width,Time,threshold)
        return {}