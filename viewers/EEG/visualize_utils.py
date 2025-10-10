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

    def create_continuous_viewer(self, channel_idx, window_start, window_length):
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
        theta = np.linspace(0, 360, len(signal))
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f"Amplitude-Time Plot",
                f"Polar Plot"
            ),
            specs=[[{"type": "scatter"}, {"type": "polar"}]]
        )
        
        # Amplitude-Time
        fig.add_trace(go.Scatter(
            x=time_axis,
            y=signal,
            mode='lines',
            name=f'{CH_LABELS[channel_idx]}',
            line=dict(color='blue', width=1)
        ),
            row=1, col=1
        )
        
        # Polar plot
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
        
        fig.update_layout(
            title=f"Continuous Signal Viewer - Channel: {CH_LABELS[channel_idx]}",
            height=400,
            template="plotly_white",
            showlegend=True
        )
        
        # Update x-axis label for amplitude plot
        fig.update_xaxes(title_text="Time (s)", row=1, col=1)
        fig.update_yaxes(title_text="Amplitude (μV)", row=1, col=1)
        fig.update_xaxes(dict(range=[time_axis[0], time_axis[-1]]))
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

    def create_crp_plot(self, ch1_idx, ch2_idx,color):
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
                colorscale=color,
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
    
    def create_xor_graph(self, channel_idx, chunk_width,Time,threshold):
        """Create XOR graph with overlapping chunks."""
        
        chunk_samples = int(chunk_width * self.dm.original_sfreq)
        Window_size = int(Time * self.dm.original_sfreq)
        n_sample = self.dm.temp_signals[channel_idx,:Window_size]
        n_chunks = n_sample.shape[0] // chunk_samples
        
        fig = go.Figure()
        
        # Initialize with first chunk
        accumulated = n_sample[:chunk_samples]
        time_axis = np.linspace(0, Time)
        
        # XOR with subsequent chunks
        for i in range(0, min(n_chunks, 5)):  # Limit to 5 chunks for visibility
            start_idx = i * chunk_samples
            end_idx = start_idx + chunk_samples
            
            if end_idx > n_sample.shape[0]:
                break
            
            chunk = n_sample[start_idx:end_idx]
            
            # Simple XOR-like operation: difference between chunks
            xor_result = np.abs(chunk - accumulated)
            accumulated = chunk.copy()
            
            threshold = threshold
            xor_result = xor_result[xor_result >= threshold]
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=xor_result,
                mode='markers',
                name=f'XOR Chunk {i}',
                marker=dict(size=4, opacity=0.7),
                showlegend=True
            ))
        
        fig.update_layout(
            title=f"XOR Graph - Channel: {CH_LABELS[channel_idx]} (Chunk width: {chunk_width}s)",
            xaxis_title="Time within chunk (s)",
            yaxis_title="XOR Amplitude (μV)",
            height=500,
            template="plotly_white",
            showlegend=True
        )
        
        return fig