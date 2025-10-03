"""
Visualization utilities for creating ECG plots
"""
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from config import (
    SAMPLING_FREQUENCY,
    MAX_RECURRENCE_SAMPLES,
    ICU_WINDOW_DURATION,
    ICU_BACKGROUND_COLOR,
    ICU_GRID_COLOR,
    ICU_SIGNAL_COLORS,
    ICU_SWEEP_LINE_COLOR,
    XOR_THRESHOLD,
    PHASE_SPACE_GRID_RESOLUTION,
    PHASE_SPACE_MIN_COUNT_DISPLAY
)
from utils.signal_processing import (
    compute_recurrence_matrix,
    downsample_signal,
    standardize_signal,
    compute_phase_space_occurrences
)


def create_phase_space_plot(signal_window, channel_1, channel_2, record_index,
                            start_idx, end_idx, fs, grid_resolution=PHASE_SPACE_GRID_RESOLUTION):
    """
    Create phase space plot showing two channels with occurrence counts

    Args:
        signal_window (np.ndarray): ECG signal window
        channel_1 (int): First channel index (X-axis)
        channel_2 (int): Second channel index (Y-axis)
        record_index (int): Record index
        start_idx (int): Start sample index
        end_idx (int): End sample index
        fs (int): Sampling frequency
        grid_resolution (float): Grid resolution for binning points

    Returns:
        go.Figure: Plotly figure object with phase space visualization
    """
    # Extract signals for the two channels
    sig_x = signal_window[:, channel_1]
    sig_y = signal_window[:, channel_2]

    # Compute occurrence counts for phase space points
    x_coords, y_coords, counts = compute_phase_space_occurrences(sig_x, sig_y, grid_resolution)

    # Filter points with minimum count
    mask = counts >= PHASE_SPACE_MIN_COUNT_DISPLAY
    x_coords = x_coords[mask]
    y_coords = y_coords[mask]
    counts = counts[mask]

    # Create figure
    fig = go.Figure()

    # Add scatter plot with text labels showing occurrence count
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=8,
            color=counts,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Occurrences"),
            line=dict(width=0.5, color='darkblue')
        ),
        text=counts,
        textposition='middle center',
        textfont=dict(size=8, color='black'),
        name='Phase Space Points',
        hovertemplate='<b>Lead %{customdata[0]}</b>: %{x:.2f} mV<br>' +
                      '<b>Lead %{customdata[1]}</b>: %{y:.2f} mV<br>' +
                      '<b>Occurrences</b>: %{text}<extra></extra>',
        customdata=np.column_stack([
            np.full(len(x_coords), channel_1 + 1),
            np.full(len(y_coords), channel_2 + 1)
        ])
    ))

    # Update layout
    title = (f"ECG Record {record_index} - Phase Space Recurrence Plot<br>"
             f"Lead {channel_1 + 1} vs Lead {channel_2 + 1}, "
             f"{start_idx / fs:.1f}-{end_idx / fs:.1f} sec")

    fig.update_layout(
        title=title,
        xaxis=dict(
            title=f"Lead {channel_1 + 1} Amplitude [mV]",
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='gray'
        ),
        yaxis=dict(
            title=f"Lead {channel_2 + 1} Amplitude [mV]",
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='gray'
        ),
        height=700,
        width=800,
        margin=dict(l=80, r=80, t=100, b=80),
        showlegend=False,
        hovermode='closest'
    )

    return fig


def create_xor_plot(signal_window, t, channel_1, channel_2, record_index,
                    start_idx, end_idx, fs, threshold=XOR_THRESHOLD):
    """
    Create XOR comparison plot showing two signals and their mismatch points

    Args:
        signal_window (np.ndarray): ECG signal window
        t (np.ndarray): Time array
        channel_1 (int): First channel index
        channel_2 (int): Second channel index
        record_index (int): Record index
        start_idx (int): Start sample index
        end_idx (int): End sample index
        fs (int): Sampling frequency
        threshold (float): Threshold for considering signals matched

    Returns:
        go.Figure: Plotly figure object with XOR visualization
    """
    # Create subplots: 2 signal plots + 1 XOR plot
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            f'Lead {channel_1 + 1}',
            f'Lead {channel_2 + 1}',
            f'XOR Mismatch (Leads {channel_1 + 1} vs {channel_2 + 1})'
        ),
        row_heights=[0.3, 0.3, 0.4]
    )

    # Extract signals
    sig_1 = signal_window[:, channel_1]
    sig_2 = signal_window[:, channel_2]

    # Plot first channel
    fig.add_trace(
        go.Scatter(
            x=t,
            y=sig_1,
            mode='lines',
            name=f'Lead {channel_1 + 1}',
            line=dict(width=2, color='blue')
        ),
        row=1,
        col=1
    )

    # Plot second channel
    fig.add_trace(
        go.Scatter(
            x=t,
            y=sig_2,
            mode='lines',
            name=f'Lead {channel_2 + 1}',
            line=dict(width=2, color='red')
        ),
        row=2,
        col=1
    )

    # Compute XOR logic: show points where signals DON'T match
    diff = np.abs(sig_1 - sig_2)
    mismatch_mask = diff > threshold

    # Get mismatch points
    mismatch_times = t[mismatch_mask]
    mismatch_values = diff[mismatch_mask]

    # Plot XOR result (only mismatch points)
    fig.add_trace(
        go.Scatter(
            x=mismatch_times,
            y=mismatch_values,
            mode='markers',
            name='Mismatch Points',
            marker=dict(
                size=4,
                color='purple',
                symbol='circle'
            )
        ),
        row=3,
        col=1
    )

    # Add threshold line
    fig.add_hline(
        y=threshold,
        line=dict(color='green', dash='dash', width=1),
        row=3,
        col=1,
        annotation_text=f'Threshold: {threshold}mV'
    )

    # Update layout
    title = f"ECG Record {record_index} - XOR Comparison, {start_idx / fs:.1f}-{end_idx / fs:.1f} sec"
    fig.update_layout(
        title=title,
        height=800,
        margin=dict(l=50, r=50, t=100, b=50),
        showlegend=True
    )

    # Update axes
    fig.update_xaxes(
        title_text="Time [s]",
        showgrid=True,
        gridcolor="lightgray",
        dtick=0.2,
        range=[t[0], t[-1]],
        row=3,
        col=1
    )

    fig.update_yaxes(title_text="Amplitude [mV]", showgrid=True, gridcolor="lightgray", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude [mV]", showgrid=True, gridcolor="lightgray", row=2, col=1)
    fig.update_yaxes(title_text="Difference [mV]", showgrid=True, gridcolor="lightgray", row=3, col=1)

    return fig


def create_icu_monitor_plot(signal_window, t, selected_channels, record_index,
                            start_idx, end_idx, fs, show_sweep_line=True):
    """
    Create ICU-style monitor with smooth scrolling effect
    """
    num_channels = len(selected_channels)
    if num_channels == 0:
        return go.Figure()

    fig = make_subplots(
        rows=num_channels,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=[f'Lead {ch + 1}' for ch in selected_channels]
    )

    for j, ch in enumerate(selected_channels):
        color = ICU_SIGNAL_COLORS[ch % len(ICU_SIGNAL_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=t,
                y=signal_window[:, ch],
                mode='lines',
                name=f'Lead {ch + 1}',
                line=dict(width=2, color=color),
                showlegend=False
            ),
            row=j + 1,
            col=1
        )

        if show_sweep_line:
            fig.add_vline(
                x=t[-1],
                line=dict(color=ICU_SWEEP_LINE_COLOR, width=2, dash='solid'),
                row=j + 1,
                col=1,
                opacity=0.6
            )

    time_window = ICU_WINDOW_DURATION
    t_min = t[0]
    t_max = t[0] + time_window

    fig.update_layout(
        title=dict(text=f"ECG Monitor - Record {record_index}", font=dict(color='#00ff00', size=20)),
        height=150 * num_channels + 100,
        margin=dict(l=60, r=30, t=80, b=50),
        paper_bgcolor=ICU_BACKGROUND_COLOR,
        plot_bgcolor=ICU_BACKGROUND_COLOR,
        font=dict(color='#00ff00', family='monospace')
    )

    fig.update_xaxes(
        title_text="Time [s]",
        title_font=dict(color='#00ff00'),
        showgrid=True,
        gridcolor=ICU_GRID_COLOR,
        gridwidth=1,
        dtick=0.2,
        range=[t_min, t_max],
        tickfont=dict(color='#00ff00'),
        row=num_channels,
        col=1
    )

    for j in range(num_channels):
        fig.update_yaxes(
            showgrid=True,
            gridcolor=ICU_GRID_COLOR,
            gridwidth=0.5,
            zeroline=True,
            zerolinecolor='#00ff00',
            zerolinewidth=1,
            showticklabels=True,
            tickfont=dict(color='#00ff00', size=10),
            title_text="mV",
            title_font=dict(color='#00ff00', size=10),
            row=j + 1,
            col=1
        )

    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(color='#00ff00', size=12, family='monospace')
        annotation['xanchor'] = 'left'
        annotation['x'] = 0.01

    return fig


def create_static_dynamic_plot(signal_window, t, selected_channels, record_index,
                                start_idx, end_idx, fs, mode='static'):
    """
    Create static or dynamic multi-lead ECG plot
    """
    num_channels = len(selected_channels)
    if num_channels == 0:
        return go.Figure()

    fig = make_subplots(rows=num_channels, cols=1, shared_xaxes=True, vertical_spacing=0)

    for j, ch in enumerate(selected_channels):
        fig.add_trace(
            go.Scatter(x=t, y=signal_window[:, ch], mode='lines', name=f'Lead {ch + 1}', line=dict(width=1)),
            row=j + 1, col=1
        )

    title = f"ECG Record {record_index}, {start_idx / fs:.1f}-{end_idx / fs:.1f} sec"
    fig.update_layout(title=title, height=150 * num_channels + 200, margin=dict(l=50, r=50, t=50, b=50), showlegend=True)

    fig.update_xaxes(title_text="Time [s]", showgrid=True, gridcolor="white", gridwidth=0.5, dtick=0.2, range=[t[0], t[-1]], row=num_channels, col=1)

    for j in range(num_channels):
        fig.update_yaxes(showgrid=True, gridcolor="LightPink", zeroline=True, zerolinecolor="grey", showticklabels=True, row=j + 1, col=1)

    return fig


def create_polar_plot(signal_window, selected_channels, record_index, start_idx, end_idx, fs):
    """
    Create polar plot of ECG signals
    """
    fig = go.Figure()

    for ch in selected_channels:
        theta = np.linspace(0, 2 * np.pi, len(signal_window))
        r = standardize_signal(signal_window[:, ch])

        fig.add_trace(go.Scatterpolar(
            r=r, theta=theta * 180 / np.pi, mode='lines', name=f'Lead {ch + 1}', line=dict(width=1)
        ))

    title = f"ECG Record {record_index} - Polar View, {start_idx / fs:.1f}-{end_idx / fs:.1f} sec"
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(visible=True, title="Amplitude (standardized)", range=[-10, 10]),
            angularaxis=dict(visible=True, rotation=90, direction="counterclockwise")
        ),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=True
    )

    return fig