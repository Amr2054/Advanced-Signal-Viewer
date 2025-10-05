from .app_callbacks import register_SAR_drone_callback

def register_all_callback_eeg(app):

    register_SAR_drone_callback(app)

__all__ = [
    'register_SAR_drone_callback'
]