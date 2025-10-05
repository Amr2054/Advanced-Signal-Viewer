"""
Callbacks package initialization for ECG Viewer
"""
from .interval import register_interval_callbacks
from .ui_control import register_ui_callbacks
from .graph import register_graph_callbacks


def register_all_callbacks(app, data_loader, predictor):
    """
    Register all application callbacks

    Args:
        app: Dash application instance
        data_loader: ECGDataLoader instance
        predictor: ECGPredictor instance
    """
    register_interval_callbacks(app)
    register_ui_callbacks(app)
    register_graph_callbacks(app, data_loader, predictor)


__all__ = [
    'register_interval_callbacks',
    'register_ui_callbacks',
    'register_graph_callbacks',
    'register_all_callbacks'
]