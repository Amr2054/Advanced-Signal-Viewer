"""
Main graph update callback
"""
import dash
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State
from config import (
    SAMPLING_FREQUENCY,
    STATIC_DURATION,
    ICU_WINDOW_DURATION,
    ICU_SCROLL_STEP,
    XOR_WINDOW_DURATION,
    PHASE_SPACE_WINDOW_DURATION,
    DEFAULT_LEAD_X,
    DEFAULT_LEAD_Y,
    DEFAULT_XOR_CHANNEL_1,
    DEFAULT_XOR_CHANNEL_2,
    DEFAULT_PHASE_SPACE_CHANNEL_1,
    DEFAULT_PHASE_SPACE_CHANNEL_2
)
from utils.signal_processing import get_heartbeat_info
from utils.visualization import (
    create_static_dynamic_plot,
    create_polar_plot,
    create_icu_monitor_plot,
    create_xor_plot,
    create_phase_space_plot
)


def register_graph_callbacks(app, data_loader, predictor):
    """
    Register the main graph update callback

    Args:
        app: Dash application instance
        data_loader: ECGDataLoader instance
        predictor: ECGPredictor instance
    """
    @app.callback(
        [
            Output("ecg-graph", "figure"),
            Output("diagnosis-output", "children"),
            Output("bpm-output", "children")
        ],
        [
            Input("interval", "n_intervals"),
            Input("channel-select", "value"),
            Input("mode-select", "value"),
            Input("diagnose-btn", "n_clicks"),
            Input("record-select", "value"),
            Input("xor-channel-1", "value"),
            Input("xor-channel-2", "value"),
            Input("xor-threshold", "value"),
            Input("phase-space-channel-1", "value"),
            Input("phase-space-channel-2", "value"),
            Input("phase-space-resolution", "value")
        ],
        [
            State("diagnosis-output", "children"),
            State("bpm-output", "children")
        ]
    )
    def update_graph_and_diagnosis(n_intervals, selected_channels, mode, diagnose_clicks,
                                   record_index, xor_ch1, xor_ch2, xor_threshold,
                                   phase_ch1, phase_ch2, phase_resolution,
                                   current_diagnosis, current_bpm):
        """
        Update ECG graph and handle diagnosis requests

        Args:
            n_intervals (int): Number of interval ticks
            selected_channels (list): Selected channel indices
            mode (str): Current view mode
            diagnose_clicks (int): Number of diagnose button clicks
            record_index (int): Selected record index
            xor_ch1 (int): First channel for XOR mode
            xor_ch2 (int): Second channel for XOR mode
            xor_threshold (float): XOR threshold
            phase_ch1 (int): First channel for Phase Space mode
            phase_ch2 (int): Second channel for Phase Space mode
            phase_resolution (float): Phase space grid resolution
            current_diagnosis (str): Current diagnosis text
            current_bpm (str): Current BPM text

        Returns:
            tuple: (figure, diagnosis_text, bpm_text)
        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        # Set default values for selections
        if xor_ch1 is None:
            xor_ch1 = DEFAULT_XOR_CHANNEL_1
        if xor_ch2 is None:
            xor_ch2 = DEFAULT_XOR_CHANNEL_2
        if phase_ch1 is None:
            phase_ch1 = DEFAULT_PHASE_SPACE_CHANNEL_1
        if phase_ch2 is None:
            phase_ch2 = DEFAULT_PHASE_SPACE_CHANNEL_2
        if phase_resolution is None:
            phase_resolution = 0.1

        # Get signal data
        metadata, signal, signal_scaled, target = data_loader.get_record(record_index)

        # Update BPM when record changes
        if triggered_id == "record-select":
            _, _, bpm = get_heartbeat_info(signal, SAMPLING_FREQUENCY, lead=1)
            bpm_text = f"BPM: {bpm:.1f}" if bpm else "BPM: N/A"
        else:
            bpm_text = current_bpm if current_bpm else "BPM: N/A"

        # Handle diagnosis request
        if triggered_id == "diagnose-btn" and diagnose_clicks > 0:
            result = predictor.predict(metadata, signal_scaled)
            if result['success']:
                current_diagnosis = f"Diagnosis: {result['label']} (Confidence: {result['confidence']:.2f})"
            else:
                current_diagnosis = f"Diagnosis Error: {result['error']}"

        # Return empty figure if no channels selected (except for modes that don't use channel-select)
        if not selected_channels and mode not in ['xor_mode', 'phase_space']:
            return go.Figure(), current_diagnosis or "", bpm_text

        # Calculate window parameters based on mode
        fs = SAMPLING_FREQUENCY

        if mode == 'static':
            # Static mode: show first 10 seconds
            window_size = int(STATIC_DURATION * fs)
            start_idx = 0
            end_idx = min(window_size, len(signal))

        elif mode == 'icu_monitor':
            # ICU Monitor: smooth scrolling window
            window_size = int(ICU_WINDOW_DURATION * fs)
            # Calculate current position based on intervals
            current_position = (n_intervals * ICU_SCROLL_STEP) % len(signal)
            start_idx = current_position
            end_idx = min(start_idx + window_size, len(signal))
            # Handle wrap-around if we reach the end
            if end_idx >= len(signal):
                start_idx = 0
                end_idx = window_size

        elif mode in ['dynamic', 'polar']:
            # Dynamic/Polar: show one heartbeat at a time
            window_size, _, _ = get_heartbeat_info(signal, fs, lead=1)
            start_idx = (n_intervals % ((len(signal) - window_size) // window_size)) * window_size
            end_idx = min(start_idx + window_size, len(signal))
            start_idx = max(0, end_idx - window_size)

        elif mode == 'xor_mode':
            # XOR mode: show 5 seconds
            window_size = int(XOR_WINDOW_DURATION * fs)
            start_idx = 0
            end_idx = min(window_size, len(signal))

        elif mode == 'phase_space':
            # Phase Space mode: show 10 seconds
            window_size = int(PHASE_SPACE_WINDOW_DURATION * fs)
            start_idx = 0
            end_idx = min(window_size, len(signal))

        else:
            # Default
            window_size = int(STATIC_DURATION * fs)
            start_idx = 0
            end_idx = min(window_size, len(signal))

        # Extract signal window and time array
        t = np.arange(start_idx, end_idx) / fs
        signal_window = signal[start_idx:end_idx, :]

        # Create appropriate visualization based on mode
        try:
            if mode == 'static':
                fig = create_static_dynamic_plot(
                    signal_window, t, selected_channels, record_index,
                    start_idx, end_idx, fs, 'static'
                )
            elif mode == 'icu_monitor':
                fig = create_icu_monitor_plot(
                    signal_window, t, selected_channels, record_index,
                    start_idx, end_idx, fs, show_sweep_line=True
                )
            elif mode == 'dynamic':
                fig = create_static_dynamic_plot(
                    signal_window, t, selected_channels, record_index,
                    start_idx, end_idx, fs, 'dynamic'
                )
            elif mode == 'polar':
                fig = create_polar_plot(
                    signal_window, selected_channels, record_index,
                    start_idx, end_idx, fs
                )
            elif mode == 'xor_mode':
                fig = create_xor_plot(
                    signal_window, t, xor_ch1, xor_ch2, record_index,
                    start_idx, end_idx, fs, xor_threshold
                )
            elif mode == 'phase_space':
                fig = create_phase_space_plot(
                    signal_window, phase_ch1, phase_ch2, record_index,
                    start_idx, end_idx, fs, phase_resolution
                )
            else:
                fig = go.Figure()

            return fig, current_diagnosis or "", bpm_text

        except Exception as e:
            error_msg = f"Error in {mode} mode: {str(e)}"
            return go.Figure(), current_diagnosis or "", bpm_text