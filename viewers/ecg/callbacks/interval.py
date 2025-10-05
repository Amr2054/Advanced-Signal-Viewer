"""
Interval control callbacks for ECG Viewer - COMPLETE VERSION
"""
from dash import Input, Output, State
from viewers.ecg.config import ICU_UPDATE_INTERVAL, CONTINUOUS_UPDATE_INTERVAL, POLAR_UPDATE_INTERVAL


def register_interval_callbacks(app):
    """Register callbacks for controlling the interval component"""

    @app.callback(
        [Output("ecg-interval", "disabled"), Output("ecg-interval", "interval")],
        [Input("ecg-mode-select", "value"),
         Input("ecg-play-pause", "n_clicks"),
         Input("ecg-continuous-playing", "data"),
         Input("ecg-continuous-speed", "value"),
         Input("ecg-polar-playing", "data")],
        State("ecg-interval", "disabled")
    )
    def toggle_interval(mode, n_clicks_old, is_continuous_playing, continuous_speed, is_polar_playing, is_disabled):
        """Control interval based on mode and playback state"""

        # Static modes - no interval
        if mode in ['static', 'xor_chunks', 'phase_space']:
            return True, 1000

        # Continuous Viewer
        if mode == 'continuous':
            if is_continuous_playing:
                adjusted_interval = int(CONTINUOUS_UPDATE_INTERVAL / continuous_speed)
                return False, adjusted_interval
            return True, CONTINUOUS_UPDATE_INTERVAL

        # Polar Graph (new)
        if mode == 'polar_new':
            if is_polar_playing:
                return False, POLAR_UPDATE_INTERVAL
            return True, POLAR_UPDATE_INTERVAL

        # ICU Monitor
        if mode == 'icu_monitor':
            if n_clicks_old == 0:
                return False, ICU_UPDATE_INTERVAL
            return not is_disabled, ICU_UPDATE_INTERVAL

        return True, 1000