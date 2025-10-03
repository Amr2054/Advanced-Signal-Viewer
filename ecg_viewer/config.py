"""
Configuration settings for the ECG Viewer application
"""
import zipfile
import pandas as pd

# Data paths
DATA_PATH = "data&model/data_2.npz"
MODEL_PATH = "data&model/model02.keras"
zip_path = "data&model/data_2.zip"


# Signal processing parameters
SAMPLING_FREQUENCY = 100  # Hz
STATIC_DURATION = 10  # seconds
RECURRENCE_DYNAMIC_WINDOW = 3  # seconds

# ICU Monitor parameters
ICU_WINDOW_DURATION = 6  # seconds visible on screen
ICU_UPDATE_INTERVAL = 100  # milliseconds (10 fps for smooth scrolling)
ICU_SCROLL_STEP = 10  # samples to advance per update (0.1 seconds at 100 Hz)

# XOR mode parameters
XOR_WINDOW_DURATION = 5  # seconds to display
XOR_THRESHOLD = 0.05  # mV threshold for considering signals "matched"

# Phase Space Recurrence parameters
PHASE_SPACE_WINDOW_DURATION = 1  # seconds to analyze
PHASE_SPACE_GRID_RESOLUTION = 0.1  # mV - bin size for grouping similar points
PHASE_SPACE_MIN_COUNT_DISPLAY = 1  # Minimum occurrence count to display

# Model parameters
MODEL_INPUT_SIZE = 1000
DIAGNOSIS_LABELS = ['NORM', 'MI', 'STTC', 'CD', 'HYP']

# Visualization parameters
MAJOR_GRID_INTERVAL = 0.2  # 200ms
MINOR_GRID_INTERVAL = 0.04  # 40ms
MAX_RECURRENCE_SAMPLES = 500

# ICU Monitor colors
ICU_BACKGROUND_COLOR = '#0a0a0a'  # Almost black
ICU_GRID_COLOR = '#1a3a1a'  # Dark green
ICU_SIGNAL_COLORS = [
    '#00ff00',  # Bright green (Lead 1)
    '#00cc00',  # Green (Lead 2)
    '#00ff66',  # Light green (Lead 3)
    '#33ff33',  # Lime green (Lead 4)
    '#66ff00',  # Yellow-green (Lead 5)
    '#00ffcc',  # Cyan-green (Lead 6)
    '#00ff99',  # Teal-green (Lead 7)
    '#99ff00',  # Chartreuse (Lead 8)
    '#00ffff',  # Cyan (Lead 9)
    '#ccff00',  # Yellow (Lead 10)
    '#00ff33',  # Spring green (Lead 11)
    '#00cc66',  # Sea green (Lead 12)
]
ICU_SWEEP_LINE_COLOR = '#ffff00'  # Yellow sweep line

# Default values
DEFAULT_LEAD_X = 0
DEFAULT_LEAD_Y = 1
DEFAULT_RECURRENCE_THRESHOLD = 0.1
DEFAULT_DOWNSAMPLE_FACTOR = 2
DEFAULT_SELECTED_CHANNELS = [0, 1]
DEFAULT_XOR_CHANNEL_1 = 0
DEFAULT_XOR_CHANNEL_2 = 1
DEFAULT_PHASE_SPACE_CHANNEL_1 = 0
DEFAULT_PHASE_SPACE_CHANNEL_2 = 1