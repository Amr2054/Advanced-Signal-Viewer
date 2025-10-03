"""
Main application entry point for ECG Viewer
"""
import dash
from data.loader import ECGDataLoader
from models.predictor import ECGPredictor
from components import create_layout
from callbacks import register_all_callbacks


def create_app():
    """
    Create and configure the Dash application

    Returns:
        dash.Dash: Configured Dash application
    """
    # Initialize Dash app
    app = dash.Dash(__name__)

    # Load data and model
    data_loader = ECGDataLoader()
    predictor = ECGPredictor()

    # Create layout
    app.layout = create_layout(
        num_records=data_loader.get_num_records(),
        num_leads=data_loader.get_num_leads()
    )

    # Register all callbacks
    register_all_callbacks(app, data_loader, predictor)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)