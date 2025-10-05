import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import h5py
import numpy as np
import base64
import io
import re
from scipy.io import wavfile
from scipy import signal
from werkzeug.utils import secure_filename
import plotly.graph_objs as go
import math
import time
from viewers.doppler.layout.doppler_layout import*


# =============================================================================
# CONSTANTS
# =============================================================================

SOUND_SPEED = 343.0  # m/s
DISPLAY_HZ = 25
START_X = -200.0
END_X = 200.0
OBSERVER_X = 0.0
TOTAL_DISTANCE = END_X - START_X

H5_FILENAME = 'viewers/doppler/speed_estimations_NN_1000-200-50-10-1_reg1e-3_lossMSE.h5'

VEHICLE_NAME_MAP = {
    "CitroenC4Picasso": "CitroenC4Picasso",
    "Mazda3": "Mazda3",
    "MercedesAMG550": "MercedesAMG550",
    "NissanQashqai": "NissanQashqai",
    "OpelInsignia": "OpelInsignia",
    "Peugeot3008": "Peugeot3008",
    "Peugeot307": "Peugeot307",
    "RenaultCaptur": "RenaultCaptur",
    "RenaultScenic": "RenaultScenic",
    "VWPassat": "VWPassat"
}


# =============================================================================
# DATA LOADING
# =============================================================================

try:
    hf = h5py.File(H5_FILENAME, 'r')
except:
    hf = None


# =============================================================================
# AUDIO GENERATION FUNCTIONS
# =============================================================================

def generate_doppler_audio(source_freq, speed_ms, lateral_offset, sample_rate=44100):
    """
    Generate stereo audio with continuously varying frequency and spatial positioning 
    based on Doppler effect. Sound moves from left to right as car passes.
    
    Parameters:
    - source_freq: Source frequency in Hz
    - speed_ms: Speed in m/s
    - lateral_offset: Lateral distance from road in meters
    - sample_rate: Audio sample rate
    
    Returns:
    - audio_data: numpy array of stereo audio samples (N, 2)
    - freq_profile: array of frequencies over time
    - time_array: array of time points
    """
    # Calculate trip duration
    if speed_ms <= 0:
        speed_ms = 0.01  # Prevent division by zero
    
    trip_duration = TOTAL_DISTANCE / speed_ms
    
    # Generate time array
    num_samples = int(trip_duration * sample_rate)
    time_array = np.linspace(0, trip_duration, num_samples)
    
    # Calculate car position at each sample
    car_positions = START_X + speed_ms * time_array
    
    # Calculate observed frequency and spatial parameters at each position
    freq_profile = np.zeros(num_samples)
    pan_profile = np.zeros(num_samples)  # -1 (left) to +1 (right)
    distance_profile = np.zeros(num_samples)
    
    for i, car_x in enumerate(car_positions):
        f_obs, _, r = compute_observed_freq(
            source_freq, speed_ms, car_x, OBSERVER_X, lateral_offset
        )
        freq_profile[i] = f_obs
        distance_profile[i] = r
        
        # Calculate stereo panning based on car position
        # When car is at START_X (left), pan = -1
        # When car is at OBSERVER_X (center), pan = 0
        # When car is at END_X (right), pan = +1
        pan_profile[i] = (car_x - OBSERVER_X) / (TOTAL_DISTANCE / 2)
        pan_profile[i] = np.clip(pan_profile[i], -1, 1)
    
    # Normalize distance for amplitude calculation (closer = louder)
    min_distance = np.min(distance_profile)
    max_distance = np.max(distance_profile)
    
    # Generate audio with varying frequency using phase accumulation
    phase = 0
    audio_mono = np.zeros(num_samples)
    
    for i in range(num_samples):
        # Current instantaneous frequency
        inst_freq = freq_profile[i]
        
        # Generate sample
        audio_mono[i] = np.sin(phase)
        
        # Update phase for next sample
        phase += 2 * np.pi * inst_freq / sample_rate
        
        # Keep phase in reasonable range to prevent numerical issues
        if phase > 2 * np.pi * 1000:
            phase = phase % (2 * np.pi)
    
    # Apply distance-based amplitude envelope (inverse square law simplified)
    amplitude_profile = np.zeros(num_samples)
    for i in range(num_samples):
        # Normalize distance to 0-1 range, then invert for amplitude
        norm_dist = (distance_profile[i] - min_distance) / max(max_distance - min_distance, 1)
        amplitude_profile[i] = 1.0 - 0.6 * norm_dist  # Reduce amplitude by up to 60% at max distance
    
    audio_mono = audio_mono * amplitude_profile
    
    # Create stereo audio with panning
    audio_stereo = np.zeros((num_samples, 2))
    
    for i in range(num_samples):
        pan = pan_profile[i]  # -1 to +1
        
        # Equal power panning law
        # pan = -1: full left (L=1, R=0)
        # pan = 0: center (L=0.707, R=0.707)
        # pan = +1: full right (L=0, R=1)
        pan_angle = (pan + 1) * np.pi / 4  # Convert to 0 to pi/2
        left_gain = np.cos(pan_angle)
        right_gain = np.sin(pan_angle)
        
        audio_stereo[i, 0] = audio_mono[i] * left_gain   # Left channel
        audio_stereo[i, 1] = audio_mono[i] * right_gain  # Right channel
    
    # Normalize audio to prevent clipping
    max_val = np.max(np.abs(audio_stereo))
    if max_val > 0:
        audio_stereo = audio_stereo * 0.8 / max_val
    
    # Convert to 16-bit PCM
    audio_data_int16 = (audio_stereo * 32767).astype(np.int16)
    
    return audio_data_int16, freq_profile, time_array


def audio_array_to_base64(audio_data, sample_rate=44100):
    """Convert audio numpy array to base64 encoded WAV string."""
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)
    audio_base64 = base64.b64encode(buffer.read()).decode()
    return f"data:audio/wav;base64,{audio_base64}"


# =============================================================================
# FREQUENCY EXTRACTION FUNCTIONS
# =============================================================================

def extract_smooth_doppler_frequencies(
    audio_data, 
    sample_rate, 
    nperseg=512, 
    freq_range=(300, 1800)
):
    """Extract dominant frequencies from audio using spectrogram analysis."""
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Normalize audio
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Compute spectrogram
    frequencies, times, Sxx = signal.spectrogram(
        audio_data,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=nperseg * 7 // 8,
        window='hann',
        scaling='density'
    )
    
    # Filter frequency range
    freq_mask = (frequencies >= freq_range[0]) & (frequencies <= freq_range[1])
    filtered_frequencies = frequencies[freq_mask]
    filtered_Sxx = Sxx[freq_mask, :]
    
    # Extract dominant frequency for each time frame
    dominant_frequencies = []
    frame_amplitudes = []
    
    for i in range(filtered_Sxx.shape[1]):
        frame_power = filtered_Sxx[:, i]
        frame_amplitudes.append(np.sum(frame_power))
        
        if np.sum(frame_power) > 0:
            peak_idx = np.argmax(frame_power)
            
            # Parabolic interpolation for sub-bin accuracy
            if 0 < peak_idx < len(frame_power) - 1:
                alpha = frame_power[peak_idx - 1]
                beta = frame_power[peak_idx]
                gamma = frame_power[peak_idx + 1]
                p = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
                freq_resolution = filtered_frequencies[1] - filtered_frequencies[0]
                precise_freq = filtered_frequencies[peak_idx] + p * freq_resolution
            else:
                precise_freq = filtered_frequencies[peak_idx]
            
            dominant_frequencies.append(precise_freq)
        else:
            dominant_frequencies.append(0)
    
    dominant_frequencies = np.array(dominant_frequencies)
    frame_amplitudes = np.array(frame_amplitudes)
    
    # Smooth frequencies with Savitzky-Golay filter
    if len(dominant_frequencies) > 10:
        window_length = min(11, len(dominant_frequencies) // 2 * 2 + 1)
        dominant_frequencies = signal.savgol_filter(
            dominant_frequencies, 
            window_length=window_length, 
            polyorder=2
        )
    
    # Find frequency at maximum amplitude
    max_amp_idx = np.argmax(frame_amplitudes)
    freq_at_max_amp = dominant_frequencies[max_amp_idx]
    time_at_max_amp = times[max_amp_idx]
    
    return (
        dominant_frequencies, 
        times, 
        frame_amplitudes, 
        freq_at_max_amp, 
        time_at_max_amp
    )


def wav_contents_to_freq_array(contents, nperseg=512):
    """Convert uploaded WAV file contents to frequency analysis data."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    sample_rate, audio_data = wavfile.read(io.BytesIO(decoded))
    
    freqs, times, amplitudes, freq_at_max_amp, time_at_max_amp = \
        extract_smooth_doppler_frequencies(audio_data, sample_rate, nperseg)
    
    return (
        audio_data, 
        sample_rate, 
        freqs, 
        times, 
        amplitudes, 
        freq_at_max_amp, 
        time_at_max_amp
    )


# =============================================================================
# DOPPLER SIMULATOR FUNCTIONS
# =============================================================================

def compute_observed_freq(source_f, speed_ms, car_x, observer_x, lateral):
    """Calculate observed frequency using Doppler effect equations."""
    dx = observer_x - car_x
    r = math.hypot(dx, lateral)
    
    # Calculate radial velocity component
    v_radial = 0 if r == 0 else speed_ms * (dx / r)
    
    # Doppler formula: f_obs = f_source * (c / (c - v_radial))
    denom = SOUND_SPEED - v_radial
    if abs(denom) < 1e-9:
        denom = math.copysign(1e-9, denom)
    
    f_obs = source_f * (SOUND_SPEED / denom)
    
    return f_obs, v_radial, r

def compute_source_frequency(filename, freq_at_max_amp):
    """Compute source frequency from filename and observed frequency."""
    if hf is None:
        return "H5 file not available"
    
    basename = secure_filename(filename)
    match = re.match(r"([A-Za-z0-9]+)_(\d+)", basename)
    
    if not match:
        return "Invalid filename format"
    
    vehicle_name, gt_speed_str = match.groups()
    gt_speed = int(gt_speed_str)
    
    if vehicle_name not in VEHICLE_NAME_MAP:
        return "Vehicle not in dataset"
    
    vehicle_h5_key = VEHICLE_NAME_MAP[vehicle_name]
    
    try:
        speed_est = np.array(hf[vehicle_h5_key + '_speeds_est_all'], dtype=np.float64)
        speed_gt = np.array(hf[vehicle_h5_key + '_speeds_gt'], dtype=int)
    except:
        return "Data not found in H5 file"
    
    if gt_speed not in speed_gt:
        return "GT speed not found in H5"
    
    # Get predicted speed
    gt_index = np.where(speed_gt == gt_speed)[0][0]
    predicted_speed_kmh = speed_est[19][gt_index]
    predicted_speed_ms = predicted_speed_kmh / 3.6
    
    # Doppler formula: f_source = f_observed * (c - v) / c
    source_freq = freq_at_max_amp * (SOUND_SPEED - predicted_speed_ms) / SOUND_SPEED
    
    return (
        f"Estimated source frequency: {source_freq:.2f} Hz "
        f"(using predicted speed {predicted_speed_kmh:.2f} km/h)"
    )

def get_initial_animation_state():
    """Return initial animation state."""
    style = {
        'position': 'absolute',
        'left': '10%',
        'top': '36%',
        'fontSize': '40px'
    }
    return (
        True,
        'stopped',
        '0',
        f"{START_X:.1f} m",
        "0.00 s",
        "--- Hz",
        "Click START",
        style
    )


def handle_start_stop(anim_state, speed_val, speed_unit, speed_ms, 
                      lateral, source_f):
    """Handle start/stop button press."""
    style = {
        'position': 'absolute',
        'left': '10%',
        'top': '36%',
        'fontSize': '40px'
    }
    
    if anim_state == 'stopped':
        # Start animation
        ts = time.time()
        car_x0 = START_X
        f0, _, _ = compute_observed_freq(source_f, speed_ms, car_x0, OBSERVER_X, lateral)
        
        info = (
            f"Started. speed={speed_val} {speed_unit} "
            f"({speed_ms:.2f} m/s), lateral={lateral} m"
        )
        
        return (
            False,
            'running',
            str(ts),
            f"{car_x0:.1f} m",
            "0.00 s",
            f"{f0:.2f} Hz",
            info,
            style
        )
    else:
        # Stop animation
        return (
            True,
            'stopped',
            '0',
            f"{START_X:.1f} m",
            "0.00 s",
            "--- Hz",
            "Stopped",
            style
        )


def handle_animation_step(start_ts, n_intervals, speed_ms, source_f, lateral):
    """Handle animation step during running state."""
    # Calculate elapsed time
    try:
        ts = float(start_ts)
        t = time.time() - ts
    except:
        t = n_intervals / DISPLAY_HZ
    
    # Calculate car position
    car_x = START_X + speed_ms * t
    
    # Check if trip is finished
    if speed_ms > 0 and car_x >= END_X:
        style = {
            'position': 'absolute',
            'left': '10%',
            'top': '36%',
            'fontSize': '40px'
        }
        trip_duration = (END_X - START_X) / max(speed_ms, 1e-9)
        return (
            True,
            'stopped',
            '0',
            f"{END_X:.1f} m",
            f"{trip_duration:.2f} s",
            "--- Hz",
            "Trip finished",
            style
        )
    
    # Calculate observed frequency
    f_obs, v_radial, r = compute_observed_freq(
        source_f, speed_ms, car_x, OBSERVER_X, lateral
    )
    
    # Update car position on screen
    frac = (car_x - START_X) / TOTAL_DISTANCE
    left_pct = 10 + frac * 80
    
    style = {
        'position': 'absolute',
        'left': f'{left_pct}%',
        'top': '36%',
        'fontSize': '40px'
    }
    
    info = (
        f"car_x={car_x:.1f} m | t={t:.2f}s | "
        f"v_radial={v_radial:.3f} m/s | slant_r={r:.1f} m | "
        f"source={source_f:.1f} Hz"
    )
    
    return (
        False,
        'running',
        start_ts,
        f"{car_x:.1f} m",
        f"{t:.2f} s",
        f"{f_obs:.3f} Hz",
        info,
        style
    )

# =============================================================================
# CALLBACKS
# =============================================================================
def doppler_callbacks(app):
    @app.callback(
        Output('doppler-content', 'children'),
        Input('url', 'pathname'),
    )
    def display_page(pathname):

        """Route to appropriate page based on URL."""
        if pathname == "/doppler-viewer/detection":
            return create_detection_layout()
        elif pathname == "/doppler-viewer/generation":
            return create_generation_layout()
        else:
            return html.Div([html.H3("Welcome! Select an option above.")])


    @app.callback(
        Output('audio-player-container', 'children'),
        Input('generate-audio-button', 'n_clicks'),
        [
            State('source-freq', 'value'),
            State('speed-input', 'value'),
            State('speed-unit', 'value'),
            State('lateral-input', 'value')
        ],
        prevent_initial_call=True
    )
    def generate_audio(n_clicks, source_freq, speed_input, speed_unit, lateral_offset):
        """Generate Doppler effect audio."""
        if n_clicks == 0:
            return html.Div()
        
        try:
            # Parse inputs
            source_f = float(source_freq) if source_freq else 800.0
            lateral = float(lateral_offset) if lateral_offset else 30.0
            speed_val = float(speed_input) if speed_input else 60.0
            speed_ms = speed_val / 3.6 if speed_unit == 'kmh' else speed_val
            
            # Generate audio
            audio_data, freq_profile, time_array = generate_doppler_audio(
                source_f, speed_ms, lateral
            )
            
            # Convert to base64 for audio player
            audio_base64 = audio_array_to_base64(audio_data)
            
            # Calculate trip info
            trip_duration = time_array[-1]
            min_freq = np.min(freq_profile)
            max_freq = np.max(freq_profile)
            
            # Create audio player with info
            audio_player = html.Div([
                html.H4("Generated Doppler Audio (Stereo)", style={'color': 'green'}),
                html.P(f"Trip Duration: {trip_duration:.2f}s | "
                    f"Frequency Range: {min_freq:.1f} Hz → {max_freq:.1f} Hz → {min_freq:.1f} Hz"),
                html.P("🎧 Use headphones for best spatial effect!", style={'fontStyle': 'italic', 'color': '#666'}),
                html.Audio(
                    src=audio_base64,
                    controls=True,
                    style={'width': '80%'}
                )
            ])
            
            return audio_player
            
        except Exception as e:
            error_msg = html.Div([
                html.H4("Error Generating Audio", style={'color': 'red'}),
                html.P(f"Error: {str(e)}")
            ])
            return error_msg


    @app.callback(
        [
            Output('waveform-graph', 'figure'),
            Output('file-info', 'children'),
            Output('max-freq', 'children'),
            Output('source-freq-display', 'children')
        ],
        Input('upload-wav', 'contents'),
        State('upload-wav', 'filename')
    )
    def update_detection_output(contents, filename):
        """Process uploaded WAV file and display analysis results."""
        if contents is None:
            return go.Figure(), "No file uploaded", "", ""
        
        try:
            # Extract frequency data from WAV
            audio_data, sample_rate, freqs, times, amplitudes, \
                freq_at_max_amp, time_at_max_amp = wav_contents_to_freq_array(contents)
            
            # Prepare waveform data
            audio_time = np.arange(len(audio_data)) / float(sample_rate)
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
            
            # Create waveform plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=audio_time,
                y=audio_data,
                mode='lines',
                line=dict(color='blue'),
                name='Signal'
            ))
            fig.update_layout(
                title=f"Waveform of {filename}",
                xaxis_title="Time [s]",
                yaxis_title="Amplitude",
                height=500
            )
            
            # Display file information
            file_info = (
                f"Sample rate: {sample_rate} Hz, "
                f"Total samples: {len(audio_data)}"
            )
            
            max_freq_text = (
                f"Observed frequency at max amplitude: "
                f"{freq_at_max_amp:.2f} Hz at {time_at_max_amp:.2f}s"
            )
            
            # Compute source frequency using predicted speed
            source_freq_text = compute_source_frequency(
                filename,
                freq_at_max_amp
            )
            
            return fig, file_info, max_freq_text, source_freq_text
        
        except Exception as e:
            return go.Figure(), f"Error reading WAV: {str(e)}", "", ""

    @app.callback(
        [
            Output('interval', 'disabled'),
            Output('animation-state', 'children'),
            Output('start-ts', 'children'),
            Output('car-pos-display', 'children'),
            Output('time-display', 'children'),
            Output('freq-display', 'children'),
            Output('info', 'children'),
            Output('car-emoji', 'style')
        ],
        [
            Input('start-button', 'n_clicks'),
            Input('interval', 'n_intervals')
        ],
        [
            State('animation-state', 'children'),
            State('speed-input', 'value'),
            State('speed-unit', 'value'),
            State('source-freq', 'value'),
            State('lateral-input', 'value'),
            State('start-ts', 'children')
        ]
    )
    def update_animation(
        n_clicks,
        n_intervals,
        anim_state,
        speed_input,
        speed_unit,
        source_freq,
        lateral_offset,
        start_ts
    ):
        """Update animation state and car position."""
        ctx = dash.callback_context
        
        # Initial state
        if not ctx.triggered:
            return get_initial_animation_state()
        
        # Parse trigger
        trig = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Parse inputs with defaults
        try:
            source_f = float(source_freq)
            lateral = float(lateral_offset)
            speed_val = float(speed_input)
        except:
            source_f, lateral, speed_val = 800.0, 30.0, 60.0
        
        speed_ms = speed_val / 3.6 if speed_unit == 'kmh' else speed_val
        
        # Handle start/stop button
        if trig == 'start-button':
            return handle_start_stop(anim_state, speed_val, speed_unit, speed_ms, 
                                    lateral, source_f)
        
        # Handle animation step
        if trig == 'interval' and anim_state == 'running':
            return handle_animation_step(start_ts, n_intervals, speed_ms, 
                                        source_f, lateral)
        
        return dash.no_update