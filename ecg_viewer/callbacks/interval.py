"""
Interval control callbacks
"""
from dash import Input, Output, State
from config import ICU_UPDATE_INTERVAL


def register_interval_callbacks(app):
    """
    Register callbacks for controlling the interval component

    Args:
        app: Dash application instance
    """
    @app.callback(
        [Output("interval", "disabled"), Output("interval", "interval")],
        Input("mode-select", "value"),
        Input("play-pause", "n_clicks"),
        State("interval", "disabled")
    )
    def toggle_interval(mode, n_clicks, is_disabled):
        """
        Control interval component based on mode and play/pause button

        Args:
            mode (str): Current view mode
            n_clicks (int): Number of times play/pause button clicked
            is_disabled (bool): Current interval disabled state

        Returns:
            tuple: (disabled, interval) - Whether interval should be disabled and interval duration
        """
        # Static modes don't need interval
        if mode in ['static', 'xor_mode', 'phase_space']:
            return True, 1000

        # ICU Monitor mode uses fast update interval
        if mode == 'icu_monitor':
            if n_clicks == 0:
                return False, ICU_UPDATE_INTERVAL
            return not is_disabled, ICU_UPDATE_INTERVAL

        # Polar mode uses standard interval
        if mode == 'polar':
            if n_clicks == 0:
                return False, 1000
            return not is_disabled, 1000

        # Other dynamic modes use standard interval
        if mode in ['dynamic']:
            if n_clicks == 0:
                return False, 1000
            return not is_disabled, 1000

        return True, 1000