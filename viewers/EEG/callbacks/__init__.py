from .app_callbacks import app_callbacks

def register_all_callback_eeg(app):

    app_callbacks(app)

__all__ = [
    'app_callbacks'
]