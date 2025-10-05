from .doppler_callbacks import doppler_callbacks

def register_all_callback_eeg(app):

    doppler_callbacks(app)

__all__ = [
    'doppler_callbacks'
]