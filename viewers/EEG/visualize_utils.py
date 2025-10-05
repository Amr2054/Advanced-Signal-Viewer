import os
import numpy as np
import logging

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yaml
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path (change on your device)
Path = 'viewers/EEG/'

# -------- Load Configs --------
with open(f"{Path}config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# -----------------------
# Constants
# -----------------------
DOWNSAMPLING_FACTOR = config['DOWNSAMPLING_FACTOR']
SFREQ = config['SFREQ']
CH_LABELS = config['CH_LABELS']
SEGMENT_SIZE = config['SEGMENT_SIZE']


# -----------------------
# Plot Generator Class
# -----------------------
class PlotGenerator:
    """Generates various plots for the dashboard."""

    def __init__(self, data_manager):
        self.dm = data_manager

    def create_continuous_viewer(self, channel_idx, window_start, window_length, show_predictions=True):
        """Create continuous-time signal viewer with viewport control."""

        # Calculate sample indices
        start_sample = int(window_start * self.dm.original_sfreq)
        window_samples = int(window_length * self.dm.original_sfreq)
        end_sample = min(start_sample + window_samples, self.dm.total_samples)

        # Ensure valid range
        if start_sample >= self.dm.total_samples:
            start_sample = self.dm.total_samples - window_samples
        if start_sample < 0:
            start_sample = 0

        # Get signal for selected channel
        signal = self.dm.temp_signals[channel_idx, start_sample:end_sample]
        time_axis = self.dm.time_axis[start_sample:end_sample]

        fig = go.Figure()

        # Add main signal trace
        fig.add_trace(go.Scatter(
            x=time_axis,
            y=signal,
            mode='lines',
            name=f'{CH_LABELS[channel_idx]}',
            line=dict(color='blue', width=1)
        ))

        # Add seizure annotations if enabled
        if show_predictions:
            for pred in self.dm.segment_predictions:
                if pred['is_seizure']:
                    seg = self.dm.segments[pred['segment']]
                    # Check if this segment is visible in current window
                    if seg['end_time'] >= window_start and seg['start_time'] <= (window_start + window_length):
                        fig.add_vrect(
                            x0=seg['start_time'], x1=seg['end_time'],
                            fillcolor="red", opacity=0.2,
                            layer="below", line_width=0
                        )

        fig.update_layout(
            title=f"Continuous Signal Viewer - Channel: {CH_LABELS[channel_idx]}",
            xaxis_title="Time (s)",
            yaxis_title="Amplitude (μV)",
            height=400,
            template="plotly_white",
            xaxis=dict(range=[time_axis[0], time_axis[-1]]),
            showlegend=True
        )

        return fig

    def create_segment_plots(self, segment_idx, channel_idx):
        """Create amplitude-time and polar plots for a specific segment."""

        if segment_idx >= len(self.dm.segments):
            return go.Figure(), go.Figure()

        segment = self.dm.segments[segment_idx]
        prediction = self.dm.segment_predictions[segment_idx]

        # Get signal for selected channel
        signal = segment['data'][channel_idx, :]
        time_axis = np.linspace(segment['start_time'], segment['end_time'], len(signal))

        # Create subplot figure with both plots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f"Amplitude-Time Plot (Segment {segment_idx})",
                f"Polar Plot (Segment {segment_idx})"
            ),
            specs=[[{"type": "scatter"}, {"type": "polar"}]]
        )

        # Amplitude-time plot
        fig.add_trace(
            go.Scatter(
                x=time_axis,
                y=signal,
                mode="lines",
                name=f"{CH_LABELS[channel_idx]}",
                line=dict(width=1.5, color='blue')
            ),
            row=1, col=1
        )

        # Polar plot
        theta = np.linspace(0, 360, len(signal))
        fig.add_trace(
            go.Scatterpolar(
                r=signal,
                theta=theta,
                mode="lines",
                name=f"Polar {CH_LABELS[channel_idx]}",
                line=dict(width=1, color='green')
            ),
            row=1, col=2
        )

        # Update layout
        status_color = '#ff4444' if prediction['is_seizure'] else '#44ff44'
        status_text = "SEIZURE DETECTED" if prediction['is_seizure'] else "NORMAL"

        fig.update_layout(
            title={
                'text': f"Channel: {CH_LABELS[channel_idx]} | Status: {status_text} (Prob: {prediction['prediction']:.3f})",
                'font': {'size': 18, 'color': status_color}
            },
            height=500,
            showlegend=False,
            template="plotly_white"
        )

        # Update x-axis label for amplitude plot
        fig.update_xaxes(title_text="Time (s)", row=1, col=1)
        fig.update_yaxes(title_text="Amplitude (μV)", row=1, col=1)

        return fig

    def create_crp_plot(self, ch1_idx, ch2_idx):
        """Cross recurrence matrix for the entire signal."""

        signals = self.dm.temp_signals
        amps = np.round(np.column_stack(
            (signals[ch1_idx, :], signals[ch2_idx, :])
        ), -2)

        unique_points, counts = np.unique(amps, axis=0, return_counts=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=unique_points[:, 0],
            y=unique_points[:, 1],
            mode="markers",
            marker=dict(
                size=5,
                color=counts,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Count")
            ),
            text=counts,
            hovertemplate='%{text}<extra></extra>'
        ))

        fig.update_layout(
            title=f"Cross Recurrence Plot: {CH_LABELS[ch1_idx]} vs {CH_LABELS[ch2_idx]} (Entire Signal)",
            xaxis_title=f"{CH_LABELS[ch2_idx]} Amplitude (μV)",
            yaxis_title=f"{CH_LABELS[ch1_idx]} Amplitude (μV)",
            width=700, height=700,
            template="plotly_white"
        )
        return fig

    def create_summary_plot(self):
        """Create a summary plot showing all predictions."""

        segments = list(range(len(self.dm.segment_predictions)))
        predictions = [p['prediction'] for p in self.dm.segment_predictions]
        colors = ['red' if p > 0.5 else 'green' for p in predictions]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=segments,
            y=predictions,
            marker_color=colors,
            text=[f"{p:.3f}" for p in predictions],
            textposition='outside',
            hovertemplate='Segment %{x}<br>Probability: %{y:.3f}<extra></extra>'
        ))

        # Add threshold line
        fig.add_hline(y=0.5, line_dash="dash", line_color="black",
                      annotation_text="Seizure Threshold (0.5)")

        fig.update_layout(
            title="Seizure Detection Results for All Segments",
            xaxis_title="Segment Index",
            yaxis_title="Seizure Probability",
            height=400,
            showlegend=False,
            template="plotly_white",
            yaxis=dict(range=[0, 1])
        )

        return fig