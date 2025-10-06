from dash import Input, Output, State
import dash


def register_ui_callbacks(app):
    """Register all UI control callbacks"""

    # Show/hide mode-specific controls
    @app.callback(
        [Output("ecg-continuous-controls", "style"),
         Output("ecg-xor-chunks-controls", "style"),
         Output("ecg-polar-controls", "style"),
         Output("ecg-phase-space-controls", "style")],
        Input("ecg-mode-select", "value")
    )
    def show_mode_controls(mode):
        """Show/hide controls based on selected mode"""
        continuous_style = {"display": "block"} if mode == 'continuous' else {"display": "none"}
        xor_style = {"display": "block"} if mode == 'xor_chunks' else {"display": "none"}
        polar_style = {"display": "block"} if mode == 'polar_new' else {"display": "none"}
        phase_style = {"display": "block"} if mode == 'phase_space' else {"display": "none"}

        return continuous_style, xor_style, polar_style, phase_style


    # === Continuous Viewer Controls ===
    @app.callback(Output("ecg-continuous-speed-display", "children"), Input("ecg-continuous-speed", "value"))
    def update_speed_display(speed):
        return f"{speed:.1f}x"

    @app.callback(Output("ecg-continuous-zoom-display", "children"), Input("ecg-continuous-zoom", "value"))
    def update_zoom_display(zoom):
        return f"{zoom:.1f}s"

    @app.callback(Output("ecg-continuous-position-display", "children"), Input("ecg-continuous-position", "value"))
    def update_position_display(position):
        return f"{position:.1f}s"

    @app.callback(
        [Output("ecg-continuous-position", "max"), Output("ecg-continuous-position", "marks")],
        [Input("ecg-signal-length", "data"), Input("ecg-continuous-zoom", "value")]
    )
    def update_position_slider(signal_length, zoom):
        if signal_length == 0:
            return 100, {}
        max_position = max(0, signal_length - zoom)
        step = 2 if signal_length <= 20 else (10 if signal_length <= 60 else 20)
        marks = {i: f"{i}s" for i in range(0, int(signal_length) + 1, step)}
        return max_position, marks

    @app.callback(
        [Output("ecg-continuous-playing", "data"), Output("ecg-continuous-play-pause", "children"), Output("ecg-continuous-play-pause", "color")],
        Input("ecg-continuous-play-pause", "n_clicks"),
        State("ecg-continuous-playing", "data"),
        prevent_initial_call=True
    )
    def toggle_continuous_playback(n_clicks, is_playing):
        new_state = not is_playing
        return (True, "⏸ Pause", "warning") if new_state else (False, "▶ Play", "success")

    @app.callback(Output("ecg-continuous-position", "value", allow_duplicate=True), Input("ecg-continuous-reset", "n_clicks"), prevent_initial_call=True)
    def reset_continuous_position(n_clicks):
        return 0

    @app.callback(
        Output("ecg-continuous-position", "value", allow_duplicate=True),
        Input("ecg-continuous-pan-left", "n_clicks"),
        [State("ecg-continuous-position", "value"), State("ecg-continuous-position", "max")],
        prevent_initial_call=True
    )
    def pan_left(n_clicks, current_position, max_position):
        from viewers.ecg.config import CONTINUOUS_PAN_STEP
        return max(0, current_position - CONTINUOUS_PAN_STEP)

    @app.callback(
        Output("ecg-continuous-position", "value", allow_duplicate=True),
        Input("ecg-continuous-pan-right", "n_clicks"),
        [State("ecg-continuous-position", "value"), State("ecg-continuous-position", "max")],
        prevent_initial_call=True
    )
    def pan_right(n_clicks, current_position, max_position):
        from viewers.ecg.config import CONTINUOUS_PAN_STEP
        return min(max_position, current_position + CONTINUOUS_PAN_STEP)

    # === XOR Chunks Controls ===
    @app.callback(Output("ecg-xor-chunk-period-display", "children"), Input("ecg-xor-chunk-period", "value"))
    def update_xor_period_display(period):
        return f"{period:.1f}s"

    @app.callback(Output("ecg-xor-duration-display", "children"), Input("ecg-xor-duration", "value"))
    def update_xor_duration_display(duration):
        return f"{duration:.0f}s"

    @app.callback(Output("ecg-xor-threshold-display", "children"), Input("ecg-xor-chunks-threshold", "value"))
    def update_xor_threshold_display(threshold):
        return f"{threshold:.2f}mV"

    # === Polar Controls ===
    @app.callback(Output("ecg-polar-window-display", "children"), Input("ecg-polar-window", "value"))
    def update_polar_window_display(window):
        return f"{window:.1f}s"


    @app.callback(
        [Output("ecg-polar-playing", "data"),
         Output("ecg-polar-play-pause", "children"),
         Output("ecg-polar-play-pause", "color")],
        Input("ecg-polar-play-pause", "n_clicks"),
        State("ecg-polar-playing", "data"),
        prevent_initial_call=True
    )
    def toggle_polar_playback(n_clicks, is_playing):
        new_state = not is_playing
        return (True, "⏸ Pause", "warning") if new_state else (False, "▶ Play", "success")


    @app.callback(
        [Output("ecg-polar-cumulative-data", "data", allow_duplicate=True),
         Output("ecg-polar-position", "data")],
        Input("ecg-polar-reset", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_polar_cumulative(n_clicks):
        return [], 0  # Reset

    # === Phase Space Controls ===
    @app.callback(Output("ecg-phase-resolution-display", "children"), Input("ecg-phase-space-resolution", "value"))
    def update_phase_resolution_display(resolution):
        return f"{resolution:.2f}mV"