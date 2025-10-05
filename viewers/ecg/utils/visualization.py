"""
Visualization utilities for creating ECG plots
"""
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from viewers.ecg.config import (
    SAMPLING_FREQUENCY,
    MAX_RECURRENCE_SAMPLES,
    ICU_WINDOW_DURATION,
    ICU_BACKGROUND_COLOR,
    ICU_GRID_COLOR,
    ICU_SIGNAL_COLORS,
    ICU_SWEEP_LINE_COLOR,
    #XOR_THRESHOLD,
    PHASE_SPACE_GRID_RESOLUTION,
    PHASE_SPACE_MIN_COUNT_DISPLAY
)
from viewers.ecg.utils.signal_processing import (
    compute_recurrence_matrix,
    downsample_signal,
    standardize_signal,
    compute_phase_space_occurrences
)


# def create_phase_space_plot(signal_window, channel_1, channel_2, record_index,
#                             start_idx, end_idx, fs, grid_resolution=PHASE_SPACE_GRID_RESOLUTION):
#     """
#     Create phase space plot showing two channels with occurrence counts
#
#     Args:
#         signal_window (np.ndarray): ECG signal window
#         channel_1 (int): First channel index (X-axis)
#         channel_2 (int): Second channel index (Y-axis)
#         record_index (int): Record index
#         start_idx (int): Start sample index
#         end_idx (int): End sample index
#         fs (int): Sampling frequency
#         grid_resolution (float): Grid resolution for binning points
#
#     Returns:
#         go.Figure: Plotly figure object with phase space visualization
#     """
#     # Extract signals for the two channels
#     sig_x = signal_window[:, channel_1]
#     sig_y = signal_window[:, channel_2]
#
#     # Compute occurrence counts for phase space points
#     x_coords, y_coords, counts = compute_phase_space_occurrences(sig_x, sig_y, grid_resolution)
#
#     # Filter points with minimum count
#     mask = counts >= PHASE_SPACE_MIN_COUNT_DISPLAY
#     x_coords = x_coords[mask]
#     y_coords = y_coords[mask]
#     counts = counts[mask]
#
#     # Create figure
#     fig = go.Figure()
#
#     # Add scatter plot with text labels showing occurrence count
#     fig.add_trace(go.Scatter(
#         x=x_coords,
#         y=y_coords,
#         mode='markers+text',
#         marker=dict(
#             size=8,
#             color=counts,
#             colorscale='Blues',
#             showscale=True,
#             colorbar=dict(title="Occurrences"),
#             line=dict(width=0.5, color='darkblue')
#         ),
#         text=counts,
#         textposition='middle center',
#         textfont=dict(size=8, color='white'),
#         name='Phase Space Points',
#         hovertemplate='<b>Lead %{customdata[0]}</b>: %{x:.2f} mV<br>' +
#                       '<b>Lead %{customdata[1]}</b>: %{y:.2f} mV<br>' +
#                       '<b>Occurrences</b>: %{text}<extra></extra>',
#         customdata=np.column_stack([
#             np.full(len(x_coords), channel_1 + 1),
#             np.full(len(y_coords), channel_2 + 1)
#         ])
#     ))
#
#     # Update layout
#     title = (f"ECG Record {record_index} - Phase Space Recurrence Plot<br>"
#              f"Lead {channel_1 + 1} vs Lead {channel_2 + 1}, "
#              f"{start_idx / fs:.1f}-{end_idx / fs:.1f} sec")
#
#     fig.update_layout(
#         title=title,
#         xaxis=dict(
#             title=f"Lead {channel_1 + 1} Amplitude [mV]",
#             showgrid=True,
#             gridcolor='lightgray',
#             zeroline=True,
#             zerolinecolor='gray'
#         ),
#         yaxis=dict(
#             title=f"Lead {channel_2 + 1} Amplitude [mV]",
#             showgrid=True,
#             gridcolor='lightgray',
#             zeroline=True,
#             zerolinecolor='gray'
#         ),
#         height=700,
#         width=800,
#         margin=dict(l=80, r=80, t=100, b=80),
#         showlegend=False,
#         hovermode='closest'
#     )
#
#     return fig
#
#
# def create_xor_plot(signal_window, t, channel_1, channel_2, record_index,
#                     start_idx, end_idx, fs, threshold=1):
#     """
#     Create XOR comparison plot showing two signals and their mismatch points
#
#     Args:
#         signal_window (np.ndarray): ECG signal window
#         t (np.ndarray): Time array
#         channel_1 (int): First channel index
#         channel_2 (int): Second channel index
#         record_index (int): Record index
#         start_idx (int): Start sample index
#         end_idx (int): End sample index
#         fs (int): Sampling frequency
#         threshold (float): Threshold for considering signals matched
#
#     Returns:
#         go.Figure: Plotly figure object with XOR visualization
#     """
#     # Create subplots: 2 signal plots + 1 XOR plot
#     fig = make_subplots(
#         rows=3,
#         cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.08,
#         subplot_titles=(
#             f'Lead {channel_1 + 1}',
#             f'Lead {channel_2 + 1}',
#             f'XOR Mismatch (Leads {channel_1 + 1} vs {channel_2 + 1})'
#         ),
#         row_heights=[0.3, 0.3, 0.4]
#     )
#
#     # Extract signals
#     sig_1 = signal_window[:, channel_1]
#     sig_2 = signal_window[:, channel_2]
#
#     # Plot first channel
#     fig.add_trace(
#         go.Scatter(
#             x=t,
#             y=sig_1,
#             mode='lines',
#             name=f'Lead {channel_1 + 1}',
#             line=dict(width=2, color='blue')
#         ),
#         row=1,
#         col=1
#     )
#
#     # Plot second channel
#     fig.add_trace(
#         go.Scatter(
#             x=t,
#             y=sig_2,
#             mode='lines',
#             name=f'Lead {channel_2 + 1}',
#             line=dict(width=2, color='red')
#         ),
#         row=2,
#         col=1
#     )
#
#     # Compute XOR logic: show points where signals DON'T match
#     diff = np.abs(sig_1 - sig_2)
#     mismatch_mask = diff > threshold
#
#     # Get mismatch points
#     mismatch_times = t[mismatch_mask]
#     mismatch_values = diff[mismatch_mask]
#
#     # Plot XOR result (only mismatch points)
#     fig.add_trace(
#         go.Scatter(
#             x=mismatch_times,
#             y=mismatch_values,
#             mode='markers',
#             name='Mismatch Points',
#             marker=dict(
#                 size=4,
#                 color='purple',
#                 symbol='circle'
#             )
#         ),
#         row=3,
#         col=1
#     )
#
#     # Add threshold line
#     fig.add_hline(
#         y=threshold,
#         line=dict(color='green', dash='dash', width=1),
#         row=3,
#         col=1,
#         annotation_text=f'Threshold: {threshold}mV'
#     )
#
#     # Update layout
#     title = f"ECG Record {record_index} - XOR Comparison, {start_idx / fs:.1f}-{end_idx / fs:.1f} sec"
#     fig.update_layout(
#         title=title,
#         height=800,
#         margin=dict(l=50, r=50, t=100, b=50),
#         showlegend=True
#     )
#
#     # Update axes
#     fig.update_xaxes(
#         title_text="Time [s]",
#         showgrid=True,
#         gridcolor="lightgray",
#         dtick=0.2,
#         range=[t[0], t[-1]],
#         row=3,
#         col=1
#     )
#
#     fig.update_yaxes(title_text="Amplitude [mV]", showgrid=True, gridcolor="lightgray", row=1, col=1)
#     fig.update_yaxes(title_text="Amplitude [mV]", showgrid=True, gridcolor="lightgray", row=2, col=1)
#     fig.update_yaxes(title_text="Difference [mV]", showgrid=True, gridcolor="lightgray", row=3, col=1)
#
#     return fig
#
#
# def create_icu_monitor_plot(signal_window, t, selected_channels, record_index,
#                             start_idx, end_idx, fs, show_sweep_line=True):
#     """
#     Create ICU-style monitor with smooth scrolling effect
#     """
#     num_channels = len(selected_channels)
#     if num_channels == 0:
#         return go.Figure()
#
#     fig = make_subplots(
#         rows=num_channels,
#         cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.02,
#         subplot_titles=[f'Lead {ch + 1}' for ch in selected_channels]
#     )
#
#     for j, ch in enumerate(selected_channels):
#         color = ICU_SIGNAL_COLORS[ch % len(ICU_SIGNAL_COLORS)]
#         fig.add_trace(
#             go.Scatter(
#                 x=t,
#                 y=signal_window[:, ch],
#                 mode='lines',
#                 name=f'Lead {ch + 1}',
#                 line=dict(width=2, color=color),
#                 showlegend=False
#             ),
#             row=j + 1,
#             col=1
#         )
#
#         if show_sweep_line:
#             fig.add_vline(
#                 x=t[-1],
#                 line=dict(color=ICU_SWEEP_LINE_COLOR, width=2, dash='solid'),
#                 row=j + 1,
#                 col=1,
#                 opacity=0.6
#             )
#
#     time_window = ICU_WINDOW_DURATION
#     t_min = t[0]
#     t_max = t[0] + time_window
#
#     fig.update_layout(
#         title=dict(text=f"ECG Monitor - Record {record_index}", font=dict(color='#00ff00', size=20)),
#         height=150 * num_channels + 100,
#         margin=dict(l=60, r=30, t=80, b=50),
#         paper_bgcolor=ICU_BACKGROUND_COLOR,
#         plot_bgcolor=ICU_BACKGROUND_COLOR,
#         font=dict(color='#00ff00', family='monospace')
#     )
#
#     fig.update_xaxes(
#         title_text="Time [s]",
#         title_font=dict(color='#00ff00'),
#         showgrid=True,
#         gridcolor=ICU_GRID_COLOR,
#         gridwidth=1,
#         dtick=0.2,
#         range=[t_min, t_max],
#         tickfont=dict(color='#00ff00'),
#         row=num_channels,
#         col=1
#     )
#
#     for j in range(num_channels):
#         fig.update_yaxes(
#             showgrid=True,
#             gridcolor=ICU_GRID_COLOR,
#             gridwidth=0.5,
#             zeroline=True,
#             zerolinecolor='#00ff00',
#             zerolinewidth=1,
#             showticklabels=True,
#             tickfont=dict(color='#00ff00', size=10),
#             title_text="mV",
#             title_font=dict(color='#00ff00', size=10),
#             row=j + 1,
#             col=1
#         )
#
#     for annotation in fig['layout']['annotations']:
#         annotation['font'] = dict(color='#00ff00', size=12, family='monospace')
#         annotation['xanchor'] = 'left'
#         annotation['x'] = 0.01
#
#     return fig


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


def create_continuous_plot(signal_window, t, selected_channels, record_index,
                           start_idx, end_idx, fs, window_size, speed):
    """
    Create continuous viewer plot with smooth scrolling

    Args:
        signal_window (np.ndarray): ECG signal window
        t (np.ndarray): Time array
        selected_channels (list): List of channel indices to plot
        record_index (int): Record index
        start_idx (int): Start sample index
        end_idx (int): End sample index
        fs (int): Sampling frequency
        window_size (float): Window size in seconds
        speed (float): Playback speed multiplier

    Returns:
        go.Figure: Plotly figure object
    """
    from plotly.subplots import make_subplots
    import plotly.graph_objs as go

    num_channels = len(selected_channels)
    if num_channels == 0:
        return go.Figure()

    # Create subplots
    fig = make_subplots(
        rows=num_channels,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=[f'Lead {ch + 1}' for ch in selected_channels]
    )

    # Add traces for each channel
    for j, ch in enumerate(selected_channels):
        fig.add_trace(
            go.Scatter(
                x=t,
                y=signal_window[:, ch],
                mode='lines',
                name=f'Lead {ch + 1}',
                line=dict(width=1.5, color=f'rgb({50 + ch * 20}, {100 + ch * 10}, {200 - ch * 10})'),
                showlegend=False
            ),
            row=j + 1,
            col=1
        )

    # Update layout
    title = f"ECG Record {record_index} - Continuous Viewer | {start_idx / fs:.1f}s - {end_idx / fs:.1f}s | Window: {window_size:.1f}s | Speed: {speed:.1f}x"

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14)
        ),
        height=150 * num_channels + 150,
        margin=dict(l=60, r=30, t=80, b=50),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='x unified'
    )

    # Update x-axis (only for bottom subplot)
    fig.update_xaxes(
        title_text="Time [s]",
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        dtick=0.2,
        range=[t[0], t[-1]],
        row=num_channels,
        col=1
    )

    # Update y-axes for all subplots
    for j in range(num_channels):
        fig.update_yaxes(
            title_text="mV",
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5,
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            showticklabels=True,
            row=j + 1,
            col=1
        )

    # Update subplot titles styling
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=11)
        annotation['xanchor'] = 'left'
        annotation['x'] = 0.01

    return fig

# def create_polar_plot(signal_window, selected_channels, record_index, start_idx, end_idx, fs):
#     """
#     Create polar plot of ECG signals
#     """
#     fig = go.Figure()
#
#     for ch in selected_channels:
#         theta = np.linspace(0, 2 * np.pi, len(signal_window))
#         r = standardize_signal(signal_window[:, ch])
#
#         fig.add_trace(go.Scatterpolar(
#             r=r, theta=theta * 180 / np.pi, mode='lines', name=f'Lead {ch + 1}', line=dict(width=1)
#         ))
#
#     title = f"ECG Record {record_index} - Polar View, {start_idx / fs:.1f}-{end_idx / fs:.1f} sec"
#     fig.update_layout(
#         title=title,
#         polar=dict(
#             radialaxis=dict(visible=True, title="Amplitude (standardized)", range=[-10, 10]),
#             angularaxis=dict(visible=True, rotation=90, direction="counterclockwise")
#         ),
#         height=600,
#         margin=dict(l=50, r=50, t=50, b=50),
#         showlegend=True
#     )
#
#     return fig

# ToDo


def create_xor_chunks_plot(signal, fs, channel, chunk_period, duration, threshold, record_index):
    """
    Create XOR Time Chunks plot - divide signal into chunks and overlay with XOR logic
    CORRECTED VERSION: Simpler, clearer XOR implementation

    Args:
        signal (np.ndarray): Full ECG signal
        fs (int): Sampling frequency
        channel (int): Channel index to display
        chunk_period (float): Duration of each chunk in seconds
        duration (float): Total duration to analyze in seconds
        threshold (float): Threshold for XOR erasure (mV)
        record_index (int): Record index

    Returns:
        go.Figure: Plotly figure with overlaid chunks
    """
    import numpy as np
    import plotly.graph_objs as go

    # Calculate number of samples
    chunk_samples = int(chunk_period * fs)
    duration_samples = int(duration * fs)

    # Validate
    if chunk_samples == 0 or duration_samples == 0:
        fig = go.Figure()
        fig.add_annotation(text="Invalid chunk period or duration",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Extract the duration window
    if duration_samples > len(signal):
        duration_samples = len(signal)

    signal_window = signal[:duration_samples, channel]

    # Calculate number of chunks
    num_chunks = duration_samples // chunk_samples

    if num_chunks == 0:
        fig = go.Figure()
        fig.add_annotation(text="Chunk period too large for duration",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Create time array for one chunk
    t_chunk = np.linspace(0, chunk_period, chunk_samples)

    # Extract all chunks
    chunks = []
    for i in range(num_chunks):
        start_idx = i * chunk_samples
        end_idx = start_idx + chunk_samples
        if end_idx <= len(signal_window):
            chunk = signal_window[start_idx:end_idx]
            chunks.append(chunk)

    # Create figure
    fig = go.Figure()

    # Simple XOR implementation:
    # Plot all chunks with transparency
    # Where chunks overlap and are similar (within threshold), they visually blend/cancel

    colors = [
        'blue', 'red', 'green', 'purple', 'orange',
        'brown', 'pink', 'gray', 'olive', 'cyan'
    ]

    for i, chunk in enumerate(chunks):
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatter(
            x=t_chunk,
            y=chunk,
            mode='lines',
            name=f'Chunk {i + 1}',
            line=dict(width=2, color=color),
            opacity=0.6,
            showlegend=True
        ))

    # Update layout
    fig.update_layout(
        title=f"ECG Record {record_index} - XOR Time Chunks Overlay<br>"
              f"Lead {channel + 1} | Chunk Period: {chunk_period:.1f}s | "
              f"Duration: {duration:.0f}s | {len(chunks)} chunks overlaid",
        xaxis_title="Time within Chunk [s]",
        yaxis_title="Amplitude [mV]",
        height=600,
        hovermode='x unified',
        showlegend=True
    )

    fig.update_xaxes(showgrid=True, gridcolor='lightgray', range=[0, chunk_period])
    fig.update_yaxes(showgrid=True, gridcolor='lightgray', zeroline=True, zerolinecolor='gray')

    return fig

def create_polar_new_plot(signal_window, t, channel, record_index, start_idx, end_idx,
                          fs, is_cumulative, cumulative_data):
    """
    Create corrected Polar plot where r = magnitude, θ = time

    Args:
        signal_window (np.ndarray): ECG signal window
        t (np.ndarray): Time array
        channel (int): Channel index
        record_index (int): Record index
        start_idx (int): Start sample index
        end_idx (int): End sample index
        fs (int): Sampling frequency
        is_cumulative (bool): Whether to show cumulative or latest only
        cumulative_data (list): List of previous data points for cumulative mode

    Returns:
        tuple: (figure, new_cumulative_data)
    """
    # Extract signal for selected channel
    sig = signal_window[:, channel]

    # Calculate r (magnitude) and θ (time mapped to angle)
    r = np.abs(sig)  # Magnitude is absolute value of amplitude

    # Map time to angle: 0 to 2π
    # Normalize time within the window to 0-1, then scale to 0-2π
    time_normalized = (t - t[0]) / (t[-1] - t[0]) if len(t) > 1 else np.zeros_like(t)
    theta = time_normalized * 360  # Convert to degrees for plotly

    fig = go.Figure()

    if is_cumulative:
        # Cumulative mode: add new data to history
        new_data = {'r': r.tolist(), 'theta': theta.tolist()}
        cumulative_data.append(new_data)

        # Plot all historical data with fading colors
        for i, data in enumerate(cumulative_data):
            opacity = 0.3 + (0.7 * (i / len(cumulative_data)))  # Fade older data
            fig.add_trace(go.Scatterpolar(
                r=data['r'],
                theta=data['theta'],
                mode='lines+markers',
                marker=dict(size=2),
                line=dict(width=1),
                opacity=opacity,
                showlegend=False
            ))
    else:
        # Latest mode: show only current window
        cumulative_data = []  # Reset cumulative data
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines+markers',
            marker=dict(size=3, color=r, colorscale='Viridis', showscale=True),
            line=dict(width=1.5, color='blue'),
            name=f'Lead {channel + 1}'
        ))

    # Update layout
    mode_text = "Cumulative" if is_cumulative else "Latest Window"
    fig.update_layout(
        title=f"ECG Record {record_index} - Polar Graph ({mode_text})<br>"
              f"Lead {channel + 1} | r = Magnitude, θ = Time | {start_idx / fs:.1f}s - {end_idx / fs:.1f}s",
        polar=dict(
            radialaxis=dict(
                title="Magnitude (|Amplitude|) [mV]",
                visible=True,
                range=[0, max(r) * 1.1] if len(r) > 0 else [0, 1]
            ),
            angularaxis=dict(
              #  title="Time",
                visible=True,
                rotation=90,
                direction="counterclockwise"
            )
        ),
        height=700,
        showlegend=False
    )

    return fig, cumulative_data

def create_phase_space_plot_with_colormap(signal_window, channel_1, channel_2, record_index,
                                          start_idx, end_idx, fs, grid_resolution, colormap):
    """
    Create phase space plot with user-selected colormap

    Args:
        signal_window (np.ndarray): ECG signal window
        channel_1 (int): First channel index (X-axis)
        channel_2 (int): Second channel index (Y-axis)
        record_index (int): Record index
        start_idx (int): Start sample index
        end_idx (int): End sample index
        fs (int): Sampling frequency
        grid_resolution (float): Grid resolution for binning
        colormap (str): Colormap name

    Returns:
        go.Figure: Plotly figure
    """
    from viewers.ecg.utils.signal_processing import compute_phase_space_occurrences
    from viewers.ecg.config import PHASE_SPACE_MIN_COUNT_DISPLAY

    # Extract signals
    sig_x = signal_window[:, channel_1]
    sig_y = signal_window[:, channel_2]

    # Compute occurrences
    x_coords, y_coords, counts = compute_phase_space_occurrences(sig_x, sig_y, grid_resolution)

    # Filter by minimum count
    mask = counts >= PHASE_SPACE_MIN_COUNT_DISPLAY
    x_coords = x_coords[mask]
    y_coords = y_coords[mask]
    counts = counts[mask]

    # Create figure
    fig = go.Figure()

    # Add scatter with selected colormap
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=8,
            color=counts,
            colorscale=colormap,
            showscale=True,
            colorbar=dict(title="Occurrences"),
            line=dict(width=0.5, color='darkgray')
        ),
        text=counts,
        textposition='middle center',
        textfont=dict(size=8, color='white'),
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
    title = (f"ECG Record {record_index} - Phase Space Recurrence<br>"
             f"Lead {channel_1 + 1} vs Lead {channel_2 + 1} | "
             f"Colormap: {colormap} | {start_idx / fs:.1f}-{end_idx / fs:.1f}s")

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
        margin=dict(l=80, r=80, t=120, b=80),
        showlegend=False,
        hovermode='closest'
    )

    return fig