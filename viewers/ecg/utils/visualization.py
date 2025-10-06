import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from viewers.ecg.utils.signal_processing import compute_phase_space_occurrences
from viewers.ecg.config import PHASE_SPACE_MIN_COUNT_DISPLAY



ECG_LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

def get_lead_name(lead_index):
    if lead_index < 12:
        return f'Lead {ECG_LEAD_NAMES[lead_index]}'
    else:
        return f'Lead {lead_index + 1}'

def create_static_dynamic_plot(signal_window, t, selected_channels, record_index,
                                start_idx, end_idx, fs, mode='static'):
    """
    Create static or dynamic multi-lead ECG plot
    """
    num_channels = len(selected_channels)
    if num_channels == 0:
        return go.Figure()

    fig = make_subplots(rows=num_channels, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    for j, ch in enumerate(selected_channels):
        fig.add_trace(
            go.Scatter(x=t, y=signal_window[:, ch], mode='lines', name=get_lead_name(ch), line=dict(width=1)),
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
                name=get_lead_name(ch),
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

def create_xor_chunks_plot(signal, fs, channel, chunk_period, duration, threshold, record_index):
    """
    Create XOR Time Chunks plot - XOR between consecutive chunks
    If chunks match (within threshold), they cancel out (XOR = 0, nothing plotted)
    If chunks differ, show the difference

    Args:
        signal (np.ndarray): Full ECG signal
        fs (int): Sampling frequency
        channel (int): Channel index to display
        chunk_period (float): Duration of each chunk in seconds
        duration (float): Total duration to analyze in seconds
        threshold (float): Threshold for considering points as matching (mV)
        record_index (int): Record index

    Returns:
        go.Figure: Plotly figure with XOR result
    """
    import numpy as np
    import plotly.graph_objs as go

    # Calculate samples
    chunk_samples = int(chunk_period * fs)
    duration_samples = int(duration * fs)

    if chunk_samples == 0 or duration_samples == 0:
        fig = go.Figure()
        fig.add_annotation(text="Invalid parameters", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    if duration_samples > len(signal):
        duration_samples = len(signal)

    signal_window = signal[:duration_samples, channel]

    # Calculate number of chunks
    num_chunks = duration_samples // chunk_samples

    if num_chunks < 2:
        fig = go.Figure()
        fig.add_annotation(text="Need at least 2 chunks for XOR comparison",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Time array for one chunk
    t_chunk = np.linspace(0, chunk_period, chunk_samples)

    # Extract all chunks
    chunks = []
    for i in range(num_chunks):
        start_idx = i * chunk_samples
        end_idx = start_idx + chunk_samples
        if end_idx <= len(signal_window):
            chunks.append(signal_window[start_idx:end_idx])

    fig = go.Figure()

    # XOR Logic: Compare consecutive chunks
    # For each pair of consecutive chunks, apply XOR
    for i in range(len(chunks) - 1):
        chunk1 = chunks[i]
        chunk2 = chunks[i + 1]

        # Calculate difference
        diff = np.abs(chunk1 - chunk2)

        # XOR: Only plot where difference > threshold (i.e., chunks don't match)
        # Where diff <= threshold, chunks match, XOR = 0 (don't plot)
        xor_mask = diff > threshold

        # Get points where XOR = 1 (difference exists)
        xor_times = t_chunk[xor_mask]
        xor_values = diff[xor_mask]

        if len(xor_times) > 0:
            fig.add_trace(go.Scatter(
                x=xor_times,
                y=xor_values,
                mode='markers',
                name=f'XOR: Chunk {i + 1} ⊕ Chunk {i + 2}',
                marker=dict(size=4, opacity=0.7),
                showlegend=True
            ))

    # If all XOR results are empty, show message
    if len(fig.data) == 0:
        fig.add_annotation(
            text="All chunks match within threshold!<br>(XOR result is empty)",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="green")
        )

    fig.update_layout(
        title=f"ECG Record {record_index} - XOR Between Consecutive Chunks<br>"
              f"Lead {channel + 1} | Chunk Period: {chunk_period:.1f}s | "
              f"{len(chunks)} chunks | Threshold: {threshold:.2f}mV<br>"
              f"<i>Points shown = chunks differ | Empty = chunks match</i>",
        xaxis_title="Time within Chunk [s]",
        yaxis_title="Absolute Difference [mV]",
        height=600,
        hovermode='closest',
        showlegend=True
    )

    fig.update_xaxes(showgrid=True, gridcolor='lightgray', range=[0, chunk_period])
    fig.update_yaxes(showgrid=True, gridcolor='lightgray', zeroline=True)

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