import os
import dash
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State
from viewers.ecg.config import (
    SAMPLING_FREQUENCY,
    STATIC_DURATION,
    ICU_WINDOW_DURATION,
    ICU_SCROLL_STEP,
    CONTINUOUS_DEFAULT_WINDOW,
    CONTINUOUS_UPDATE_INTERVAL,
    PHASE_SPACE_WINDOW_DURATION,
    DEFAULT_PHASE_SPACE_CHANNEL_1,
    DEFAULT_PHASE_SPACE_CHANNEL_2,
    DEFAULT_COLORMAP,
    XOR_CHUNKS_DEFAULT_PERIOD,
    XOR_CHUNKS_DEFAULT_DURATION,
    POLAR_DEFAULT_WINDOW
)
from viewers.ecg.utils.signal_processing import get_heartbeat_info
from viewers.ecg.utils.visualization import (
    create_static_dynamic_plot,
    create_continuous_plot,
    create_xor_chunks_plot,
    create_polar_new_plot,
    create_phase_space_plot_with_colormap, create_polar_time_domain_plot
)


def register_graph_callbacks(app, data_loader, predictor):
    """Register all graph callbacks"""

    # File upload handler
    @app.callback(
        [Output('ecg-upload-status', 'children'),
         Output('ecg-upload-status', 'style'),
         Output('ecg-record-select', 'options'),
         Output('ecg-record-select', 'value')],
        Input('ecg-upload-data', 'contents'),
        State('ecg-upload-data', 'filename')
    )
    def handle_file_upload(contents, filename):
        if contents is None:
            return "", {'display': 'none'}, dash.no_update, dash.no_update

        import base64
        import io

        try:
            # Decode the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Check file type
            if filename.endswith('.zip'):
                # Save temporarily and load
                temp_path = f'temp_{filename}'
                with open(temp_path, 'wb') as f:
                    f.write(decoded)
                success, message = data_loader.load_from_zip(temp_path)
                os.remove(temp_path)
            elif filename.endswith('.npz'):
                # Load from bytes
                success, message = data_loader.load_from_npz(io.BytesIO(decoded))
            else:
                return "❌ Please upload a .zip or .npz file", {'color': 'red',
                                                               'display': 'block'}, dash.no_update, dash.no_update

            if success:
                # Update record options
                num_records = data_loader.get_num_records()
                options = [{"label": f"Record {i}", "value": i} for i in range(num_records)]
                return f"✅ {message} - {num_records} records loaded", {'color': 'green',
                                                                           'display': 'block'}, options, 0
            else:
                return f"❌ {message}", {'color': 'red', 'display': 'block'}, dash.no_update, dash.no_update

        except Exception as e:
            return f"❌ Error: {str(e)}", {'color': 'red', 'display': 'block'}, dash.no_update, dash.no_update


    @app.callback(
        [Output('ecg-record-select', 'options', allow_duplicate=True),
         Output('ecg-record-select', 'value', allow_duplicate=True),
         Output('ecg-upload-status', 'children', allow_duplicate=True),
         Output('ecg-upload-status', 'style', allow_duplicate=True)],
        Input('ecg-data-source-select', 'value'),
        prevent_initial_call=True
    )
    def switch_data_source(source):
        if source == 'preloaded':
            # Reload original preloaded data
            success = data_loader.reload_original()

            if success:
                num_records = data_loader.get_num_records()
                options = [{"label": f"Record {i}", "value": i} for i in range(num_records)]
                return options, 0, f"✅ Preloaded data restored - {num_records} records", {'color': 'green',
                                                                                          'display': 'block'}
            else:
                return dash.no_update, dash.no_update, "❌ Error loading preloaded data", {'color': 'red',
                                                                                          'display': 'block'}
        else:
            # Switching to upload mode - clear status
            return dash.no_update, dash.no_update, "", {'display': 'none'}


    # Signal length store
    @app.callback(
        Output("ecg-signal-length", "data"),
        Input("ecg-record-select", "value")
    )
    def update_signal_length(record_index):
        try:
            _, signal, _, _ = data_loader.get_record(record_index)
            return len(signal) / SAMPLING_FREQUENCY
        except:
            return 0

    # Continuous position auto-advance
    @app.callback(
        Output("ecg-continuous-position", "value", allow_duplicate=True),
        [Input("ecg-interval", "n_intervals"), Input("ecg-mode-select", "value")],
        [State("ecg-continuous-position", "value"), State("ecg-continuous-position", "max"),
         State("ecg-continuous-playing", "data"), State("ecg-continuous-speed", "value")],
        prevent_initial_call=True
    )
    def update_continuous_position(n_intervals, mode, current_position, max_position, is_playing, speed):
        if mode == 'continuous' and is_playing:
            time_step = (CONTINUOUS_UPDATE_INTERVAL / 1000.0) * speed
            new_position = current_position + time_step
            return 0 if new_position >= max_position else new_position
        return dash.no_update

    @app.callback(
        Output("ecg-polar-position", "data", allow_duplicate=True),
        [Input("ecg-interval", "n_intervals"), Input("ecg-mode-select", "value")],
        [State("ecg-polar-position", "data"), State("ecg-polar-playing", "data"),
         State("ecg-signal-length", "data"), State("ecg-polar-window", "value")],
        prevent_initial_call=True
    )
    def update_polar_position(n_intervals, mode, current_position, is_playing, signal_length, window):
        """Auto-advance polar position when playing"""
        if mode == 'polar_new' and is_playing and signal_length > 0:
            # Advance by 0.1 seconds per interval
            new_position = current_position + 0.1
            max_position = signal_length - (window or 5.0)

            # Stop at end (don't loop automatically)
            if new_position >= max_position:
                return max_position
            return new_position
        return dash.no_update

    # Main graph callback
    @app.callback(
        [Output("ecg-graph", "figure"),
         Output("ecg-diagnosis-output", "children"),
         Output("ecg-bpm-output", "children"),
         Output("ecg-polar-cumulative-data", "data", allow_duplicate=True),
         Output("ecg-polar-time-graph", "figure"),
         Output("ecg-graph", "style")],
        [Input("ecg-interval", "n_intervals"),
         Input("ecg-channel-select", "value"),
         Input("ecg-mode-select", "value"),
         Input("ecg-diagnose-btn", "n_clicks"),
         Input("ecg-record-select", "value"),
         Input("ecg-continuous-position", "value"),
         Input("ecg-continuous-zoom", "value"),
         Input("ecg-continuous-speed", "value"),
         Input("ecg-xor-chunks-channel", "value"),
         Input("ecg-xor-chunk-period", "value"),
         Input("ecg-xor-duration", "value"),
         Input("ecg-xor-chunks-threshold", "value"),
         Input("ecg-polar-channel", "value"),
         Input("ecg-polar-window", "value"),
         Input("ecg-polar-mode", "value"),
         Input("ecg-polar-playing", "data"),
         Input("ecg-polar-position", "data"),
         Input("ecg-phase-space-channel-1", "value"),
         Input("ecg-phase-space-channel-2", "value"),
         Input("ecg-phase-space-resolution", "value"),
         Input("ecg-colormap-select", "value")],
        [State("ecg-diagnosis-output", "children"),
         State("ecg-bpm-output", "children"),
         State("ecg-polar-cumulative-data", "data")],
        prevent_initial_call='initial_duplicate'
    )
    def update_graph(n_intervals, selected_channels, mode, diagnose_clicks, record_index,
                     continuous_position, continuous_zoom, continuous_speed,
                     xor_channel, xor_period, xor_duration, xor_threshold,
                     polar_channel, polar_window, polar_mode, polar_playing,
                     polar_position,phase_ch1, phase_ch2, phase_resolution, colormap,
                     current_diagnosis, current_bpm, polar_cumulative):

        """Main graph update"""
        if mode == 'polar_new':
            graph_style = {
                'height': '70vh',
                'border': '2px solid #dee2e6',
                'borderRadius': '8px',
                'backgroundColor': 'white'
            }
        else:
            graph_style = {
                'height': '70vh',
                'border': '2px solid #dee2e6',
                'borderRadius': '8px',
                'backgroundColor': 'white'
            }

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # Set defaults - handle None values
        continuous_position = continuous_position if continuous_position is not None else 0
        continuous_zoom = continuous_zoom if continuous_zoom is not None else CONTINUOUS_DEFAULT_WINDOW
        continuous_speed = continuous_speed if continuous_speed is not None else 1.0
        xor_channel = xor_channel if xor_channel is not None else 0
        xor_period = xor_period if xor_period is not None else XOR_CHUNKS_DEFAULT_PERIOD
        xor_duration = xor_duration if xor_duration is not None else XOR_CHUNKS_DEFAULT_DURATION
        xor_threshold = xor_threshold if xor_threshold is not None else 0.05
        polar_channel = polar_channel if polar_channel is not None else 0
        polar_window = polar_window if polar_window is not None else POLAR_DEFAULT_WINDOW
        polar_mode = polar_mode if polar_mode is not None else 'latest'
        phase_ch1 = phase_ch1 if phase_ch1 is not None else DEFAULT_PHASE_SPACE_CHANNEL_1
        phase_ch2 = phase_ch2 if phase_ch2 is not None else DEFAULT_PHASE_SPACE_CHANNEL_2
        phase_resolution = phase_resolution if phase_resolution is not None else 0.1
        colormap = colormap if colormap is not None else DEFAULT_COLORMAP
        polar_cumulative = polar_cumulative if polar_cumulative is not None else []
        polar_position = polar_position if polar_position is not None else 0
        try:
            metadata, signal, signal_scaled, target = data_loader.get_record(record_index)
        except Exception as e:
            return go.Figure(), f"Error: {e}", "BPM: N/A", []

        # BPM
        if triggered_id == "ecg-record-select":
            _, _, bpm = get_heartbeat_info(signal, SAMPLING_FREQUENCY, lead=1)
            bpm_text = f"BPM: {bpm:.1f}" if bpm else "BPM: N/A"
        else:
            bpm_text = current_bpm if current_bpm else "BPM: N/A"

        # Diagnosis
        if triggered_id == "ecg-diagnose-btn" and diagnose_clicks > 0:
            result = predictor.predict(metadata, signal_scaled)
            if result['success']:
                current_diagnosis = f"Diagnosis: {result['label']}"
            else:
                current_diagnosis = f"Diagnosis Error: {result['error']}"

        # Channel check
        if not selected_channels and mode not in ['xor_chunks', 'polar_new', 'phase_space']:
            return go.Figure(), current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update,graph_style

        fs = SAMPLING_FREQUENCY

        try:
            # === MODE ROUTING ===
            if mode == 'static':
                window_size = int(STATIC_DURATION * fs)
                start_idx, end_idx = 0, min(window_size, len(signal))
                t = np.arange(start_idx, end_idx) / fs
                signal_window = signal[start_idx:end_idx, :]
                fig = create_static_dynamic_plot(signal_window, t, selected_channels, record_index,
                                                start_idx, end_idx, fs, 'static')
                return fig, current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update, graph_style

            elif mode == 'continuous':
                window_size = int(continuous_zoom * fs)
                start_idx = int(continuous_position * fs)
                end_idx = min(start_idx + window_size, len(signal))
                if end_idx >= len(signal):
                    end_idx, start_idx = len(signal), max(0, end_idx - window_size)
                t = np.arange(start_idx, end_idx) / fs
                signal_window = signal[start_idx:end_idx, :]
                fig = create_continuous_plot(signal_window, t, selected_channels, record_index,
                                            start_idx, end_idx, fs, continuous_zoom, continuous_speed)
                return fig, current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update, graph_style

            elif mode == 'xor_chunks':
                fig = create_xor_chunks_plot(signal, fs, xor_channel, xor_period, xor_duration,
                                            xor_threshold, record_index)
                return fig, current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update, graph_style

            elif mode == 'polar_new':
                window_size = int(polar_window * fs)

                if polar_playing:
                    # Use position-based playback
                    start_idx = int(polar_position * fs)
                    end_idx = min(start_idx + window_size, len(signal))

                    # Ensure valid window
                    if end_idx > len(signal):
                        start_idx = max(0, len(signal) - window_size)
                        end_idx = len(signal)
                else:
                    # Paused: keep current position
                    start_idx = int(polar_position * fs)
                    end_idx = min(start_idx + window_size, len(signal))

                    if end_idx > len(signal):
                        start_idx = max(0, len(signal) - window_size)
                        end_idx = len(signal)

                t = np.arange(start_idx, end_idx) / fs
                signal_window = signal[start_idx:end_idx, :]
                is_cumulative = (polar_mode == 'cumulative')

                # Create polar plot
                fig_polar, new_cumulative = create_polar_new_plot(signal_window, t, polar_channel, record_index,
                                                                  start_idx, end_idx, fs, is_cumulative,
                                                                  polar_cumulative)

                # Create time domain plot
                fig_time = create_polar_time_domain_plot(signal_window, t, polar_channel, record_index,
                                                         start_idx, end_idx, fs)

                return fig_polar, current_diagnosis or "", bpm_text, new_cumulative, fig_time, graph_style


            elif mode == 'phase_space':
                window_size = int(PHASE_SPACE_WINDOW_DURATION * fs)
                start_idx, end_idx = 0, min(window_size, len(signal))
                signal_window = signal[start_idx:end_idx, :]
                fig = create_phase_space_plot_with_colormap(signal_window, phase_ch1, phase_ch2, record_index,
                                                            start_idx, end_idx, fs, phase_resolution, colormap)
                return fig, current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update, graph_style

            else:
                return go.Figure(), current_diagnosis or "", bpm_text, polar_cumulative, dash.no_update, graph_style

        except Exception as e:
            import traceback
            traceback.print_exc()
            return go.Figure(), f"Error: {str(e)}", bpm_text, polar_cumulative,dash.no_update,graph_style