import base64
import io
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output, State,html

from viewers.SAR_Drone.models.earthquake_predictor import predict_damage
from viewers.SAR_Drone.models.audio_classifier import classify_audio


def register_SAR_drone_callback(app):
    @app.callback(
        Output('sar-result', 'children'),
        Input('upload-sar', 'contents'),
        State('upload-sar', 'filename')
    )
    def classify_sar(contents, filename):
        if contents is None:
            return html.Div("No file uploaded", className="text-muted")

        try:
            # Decode uploaded .npy file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            sar_data = np.load(io.BytesIO(decoded))

            # Validate channels (allow any height/width)
            if sar_data.ndim != 3 or sar_data.shape[0] != 4:
                return dbc.Alert(
                f"❌ Invalid shape: {sar_data.shape}. Expected (4, H, W)",
                color="danger"
                )

            # Validate dtype
            if sar_data.dtype != np.float32:
                sar_data = sar_data.astype(np.float32)

            # PREDICT
            result = predict_damage(sar_data)

            # Display result
            if result == "Damage":
                return dbc.Alert([
                    html.H4("🚨 DAMAGE DETECTED", className="alert-heading"),
                    html.Hr(),
                    html.P(f"File: {filename}"),
                    html.P("Earthquake damage identified in SAR imagery", className="mb-0")
                ], color="danger")
            else:
                return dbc.Alert([
                    html.H4("✅ No Damage", className="alert-heading"),
                    html.Hr(),
                    html.P(f"File: {filename}"),
                    html.P("No significant damage detected", className="mb-0")
                ], color="success")

        except Exception as e:
            return dbc.Alert(
                f"❌ Error processing file: {str(e)}",
                color="danger"
            )


    # Callback: audio classification
    @app.callback(
        Output('audio-result', 'children'),
        Input('upload-audio', 'contents'),
        State('upload-audio', 'filename')
    )
    def classify_audio_file(contents, filename):
        if contents is None:
            return html.Div("No file uploaded", className="text-muted")

        try:
            # Decode uploaded audio file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save temporarily (classify_audio needs file path)
            temp_path = f"temp_audio_{filename}"
            with open(temp_path, 'wb') as f:
                f.write(decoded)

            # CLASSIFY using your function
            result = classify_audio(temp_path)  # Returns: "drone", "bird", or "other"

            # Clean up temp file
            import os
            os.remove(temp_path)

            # Display result
            if result.lower() == "drone":
                return dbc.Alert([
                    html.H4("🚁 DRONE DETECTED", className="alert-heading"),
                    html.Hr(),
                    html.P(f"File: {filename}"),
                    html.P("Drone sound identified in audio", className="mb-0")
                ], color="warning")

            elif result.lower() == "bird":
                return dbc.Alert([
                    html.H4("🐦 BIRD DETECTED", className="alert-heading"),
                    html.Hr(),
                    html.P(f"File: {filename}"),
                    html.P("Bird sound identified in audio", className="mb-0")
                ], color="info")

            else:  # "other"
                return dbc.Alert([
                    html.H4("🔊 OTHER SOUND", className="alert-heading"),
                    html.Hr(),
                    html.P(f"File: {filename}"),
                    html.P("Sound classified as 'other'", className="mb-0")
                ], color="secondary")

        except Exception as e:
            return dbc.Alert(
                f"❌ Error processing audio: {str(e)}",
                color="danger"
            )
