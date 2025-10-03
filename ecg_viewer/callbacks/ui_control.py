"""
UI control callbacks
"""
from dash import Input, Output, State


def register_ui_callbacks(app):
    """
    Register callbacks for UI control elements

    Args:
        app: Dash application instance
    """
    @app.callback(
        Output("xor-options", "style"),
        Input("mode-select", "value")
    )
    def show_xor_options(mode):
        """
        Show/hide XOR plot options based on selected mode

        Args:
            mode (str): Current view mode

        Returns:
            dict: Style dictionary for XOR options div
        """
        if mode == 'xor_mode':
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        Output("phase-space-options", "style"),
        Input("mode-select", "value")
    )
    def show_phase_space_options(mode):
        """
        Show/hide Phase Space plot options based on selected mode

        Args:
            mode (str): Current view mode

        Returns:
            dict: Style dictionary for Phase Space options div
        """
        if mode == 'phase_space':
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        [Output("play-pause", "style"), Output("play-pause", "children")],
        [Input("mode-select", "value"), Input("interval", "disabled")]
    )
    def update_play_pause_button(mode, interval_disabled):
        """
        Show/hide and update play/pause button based on mode
        Only visible in ICU Monitor and Polar modes
        Button text changes based on playing state

        Args:
            mode (str): Current view mode
            interval_disabled (bool): Whether interval is disabled (paused)

        Returns:
            tuple: (style dict, button text)
        """
        # Only show button in ICU Monitor and Polar modes
        if mode in ['icu_monitor', 'polar']:
            # If interval is disabled, we're paused -> show "Play"
            # If interval is enabled, we're playing -> show "Pause"
            button_text = "Play" if interval_disabled else "Pause"
            return {"display": "inline-block"}, button_text
        else:
            return {"display": "none"}, "Pause"