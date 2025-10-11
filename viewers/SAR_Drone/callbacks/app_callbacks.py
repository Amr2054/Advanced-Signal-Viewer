import numpy as np
import base64
import io
import os
import librosa
import librosa.display
import plotly.graph_objs as go
from dash import Input, Output, State,html

from viewers.SAR_Drone.models.earthquake_predictor import predict_damage
from viewers.SAR_Drone.models.audio_classifier import classify_audio
from viewers.SAR_Drone.models.sar_analyzer import analyze_sar_file


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
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            sar_data = np.load(io.BytesIO(decoded))
            result = predict_damage(sar_data)
            return dbc.Alert(f"Result: {result}", color="info")
        except Exception as e:
            return dbc.Alert(f"❌ Error: {e}", color="danger")
    
    
    @app.callback(
        Output('audio-result', 'children'),
        Output('audio-player-div', 'children'),
        Output('spectrogram-graph', 'figure'),
        Output('spectrogram-data', 'data'),
        Input('upload-audio', 'contents'),
        State('upload-audio', 'filename')
    )
    def classify_audio_file(contents, filename):
        """Generates the waveform visualization, classification, and audio player."""
        if contents is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="rgba(0,0,0,0)",
                height=300
            )
            return (
                html.Div("No file uploaded", className="text-muted"),
                [],
                empty_fig,
                None
            )
    
        temp_path = None
        try:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            temp_path = f"temp_{filename}"
            with open(temp_path, "wb") as f:
                f.write(decoded)
    
            #classification
            result = classify_audio(temp_path)
    
            y, sr = librosa.load(temp_path, sr=22050, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            time_array = np.linspace(0, duration, num=len(y))
    
            #build a waveform
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=time_array,
                y=y,
                mode='lines',
                name='Amplitude',
                line=dict(color='blue', width=1)
            ))
            fig.update_xaxes(title_text='Time (s)', range=[0, duration])
            fig.update_yaxes(title_text='Amplitude', range=[-1.05, 1.05])
    
            # build the audio player
            b64_audio = base64.b64encode(open(temp_path, "rb").read()).decode()
            mime = "audio/wav" if filename.lower().endswith(".wav") else "audio/mpeg"
            audio_src = f"data:{mime};base64,{b64_audio}"
            audio_player = html.Audio(
                src=audio_src,
                controls=True,
                id="audio-player",
                style={"width": "100%"}
            )
    
            os.remove(temp_path)
    
            return (
                dbc.Alert(f"Classification Result: {result}", color="success"),
                [audio_player],
                fig,
                None
                # {'duration': duration} # Store duration for the synchronization cursor
            )
    
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
            empty_fig = go.Figure()
            empty_fig.update_layout(height=300)
    
            return (
                dbc.Alert(f"❌ Error during audio processing: {e}", color="danger"),
                [],
                empty_fig,
                None
            )
    
    
    @app.callback(
        [Output('vv-status', 'children'),
         Output('vv-store', 'data'),
         Output('analyze-tiff-btn', 'disabled')],
        Input('upload-vv', 'contents'),
        State('upload-vv', 'filename')
    )
    def save_vv(contents, filename):
        if contents is None:
            return "", None, True
        if ',' in contents:
            _, content_string = contents.split(',')
        else:
            content_string = contents
        decoded = base64.b64decode(content_string)
        os.makedirs("temp_tiff", exist_ok=True)
        path = os.path.join("temp_tiff", filename)
        with open(path, 'wb') as f:
            f.write(decoded)
        return f"✓ {filename}", path, False
    
    
    @app.callback(
        [Output('vh-status', 'children'),
         Output('vh-store', 'data')],
        Input('upload-vh', 'contents'),
        State('upload-vh', 'filename')
    )
    def save_vh(contents, filename):
        if contents is None:
            return "", None
        if ',' in contents:
            _, content_string = contents.split(',')
        else:
            content_string = contents
        decoded = base64.b64decode(content_string)
        os.makedirs("temp_tiff", exist_ok=True)
        path = os.path.join("temp_tiff", filename)
        with open(path, 'wb') as f:
            f.write(decoded)
        return f"✓ {filename}", path
    
    
    @app.callback(
        Output('tiff-result', 'children'),
        Input('analyze-tiff-btn', 'n_clicks'),
        [State('vv-store', 'data'),
         State('vh-store', 'data')],
        prevent_initial_call=True
    )
    def analyze_tiff(n_clicks, vv_path, vh_path):
        try:
            results = analyze_sar_file(vv_path, vh_path)
            return html.Div([
                dbc.Card([
                    dbc.CardHeader("📊 SAR Analysis Results"),
                    dbc.CardBody([
                        html.H6("Statistics:"),
                        html.Ul([html.Li(f"{k}: {v}") for k, v in results['statistics'].items()]),
                        html.Hr(),
                        html.Img(src=f"data:image/png;base64,{results['image1']}", style={'width': '100%'}),
                        html.Br(),
                        html.Img(src=f"data:image/png;base64,{results['image2']}", style={'width': '100%'})
                    ])
                ])
            ])
        except Exception as e:
            return dbc.Alert(f"❌ Error analyzing SAR: {e}", color="danger")
