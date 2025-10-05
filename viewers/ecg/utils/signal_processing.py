"""
Signal processing utilities for ECG analysis
"""
import numpy as np
from scipy.signal import find_peaks
from viewers.ecg.config import SAMPLING_FREQUENCY


def get_heartbeat_info(signal, fs=SAMPLING_FREQUENCY, lead=1, start_idx=0, end_idx=None):
    """
    Estimate heartbeat period and count heartbeats in a window

    Args:
        signal (np.ndarray): ECG signal array
        fs (int): Sampling frequency
        lead (int): Lead index to analyze
        start_idx (int): Start index of window
        end_idx (int): End index of window (None = use full signal)

    Returns:
        tuple: (window_size, num_heartbeats, bpm)
    """
    # Extract signal segment
    if end_idx is None:
        sig = signal[:, lead]
    else:
        sig = signal[start_idx:end_idx, lead]

    # Find R-peaks
    peaks, _ = find_peaks(sig, height=np.std(sig) * 0.5, distance=fs * 0.6)

    # Handle cases with too few peaks
    if len(peaks) < 2:
        return int(fs * 1.0), 1.0, 60.0

    # Calculate RR intervals and BPM
    rr_intervals = np.diff(peaks) / fs
    avg_rr = np.mean(rr_intervals) * fs
    bpm = 60.0 / np.mean(rr_intervals)

    #Calculate window size based on average heartbeat
    window_size = int(avg_rr * 1.5)

    # Count heartbeats in window
    if end_idx is not None:
        peaks = peaks + start_idx
        num_heartbeats = len([p for p in peaks if start_idx <= p < end_idx])
    else:
        num_heartbeats = 1.5

    return  window_size,num_heartbeats,bpm


# def compute_recurrence_matrix(sig_x, sig_y, epsilon):
#     """
#     Compute recurrence matrix based on Euclidean distance in 2D phase space
#
#     Args:
#         sig_x (np.ndarray): Signal from lead X
#         sig_y (np.ndarray): Signal from lead Y
#         epsilon (float): Recurrence threshold
#
#     Returns:
#         tuple: (recurrent_points_i, recurrent_points_j) - indices where recurrence occurs
#     """
#     # Compute Euclidean distance matrix
#     dx = sig_x[:, np.newaxis] - sig_x[np.newaxis, :]
#     dy = sig_y[:, np.newaxis] - sig_y[np.newaxis, :]
#     dist_matrix = np.sqrt(dx**2 + dy**2)
#
#     # Create recurrence matrix
#     recurrence_matrix = dist_matrix <= epsilon
#
#     # Get recurrent points
#     recurrent_points = np.where(recurrence_matrix)
#
#     return recurrent_points[0], recurrent_points[1]
#

def compute_phase_space_occurrences(sig_x, sig_y, grid_resolution=0.1):
    """
    Compute occurrence count for each point in phase space
    Maps (x, y) amplitude pairs to a grid and counts occurrences

    Args:
        sig_x (np.ndarray): Signal from channel X (amplitude values)
        sig_y (np.ndarray): Signal from channel Y (amplitude values)
        grid_resolution (float): Grid bin size for grouping similar points (mV)

    Returns:
        tuple: (x_coords, y_coords, counts) - coordinates and their occurrence counts
    """
    # Round coordinates to grid
    x_binned = np.round(sig_x / grid_resolution) * grid_resolution
    y_binned = np.round(sig_y / grid_resolution) * grid_resolution

    # Create dictionary to count occurrences
    point_counts = {}
    for x, y in zip(x_binned, y_binned):
        key = (x, y)
        point_counts[key] = point_counts.get(key, 0) + 1

    # Extract coordinates and counts
    x_coords = np.array([k[0] for k in point_counts.keys()])
    y_coords = np.array([k[1] for k in point_counts.keys()])
    counts = np.array(list(point_counts.values()))

    return x_coords, y_coords, counts


# def downsample_signal(signal, factor):
#     """
#     Downsample signal by given factor
#
#     Args:
#         signal (np.ndarray): Input signal
#         factor (int): Downsampling factor
#
#     Returns:
#         np.ndarray: Downsampled signal
#     """
#     if factor <= 1:
#         return signal
#     return signal[::factor]
#
#
# def standardize_signal(signal):
#     """
#     Standardize signal (zero mean, unit variance)
#
#     Args:
#         signal (np.ndarray): Input signal
#
#     Returns:
#         np.ndarray: Standardized signal
#     """
#     mean = np.mean(signal)
#     std = np.std(signal)
#     standardized = (signal - mean) / (std + 1e-6)
#     return np.clip(standardized, -10, 10)