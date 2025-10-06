
import zipfile
import pandas as pd

# Data paths
DATA_PATH = "viewers/ecg/data&model/data_specific_records.npz"
MODEL_PATH = "viewers/ecg/data&model/model02.keras"
zip_path = "viewers/ecg/data&model/data_2.zip"


# Signal processing parameters
SAMPLING_FREQUENCY = 100  # Hz
STATIC_DURATION = 10  # seconds

# Continuous Viewer parameters
CONTINUOUS_DEFAULT_WINDOW = 6  # seconds visible (default zoom level)
CONTINUOUS_MIN_WINDOW = 1  # seconds (max zoom in)
CONTINUOUS_MAX_WINDOW = 30  # seconds (max zoom out)
CONTINUOUS_DEFAULT_SPEED = 1.0  # 1x speed
CONTINUOUS_MIN_SPEED = 0.1  # 0.1x speed
CONTINUOUS_MAX_SPEED = 5.0  # 5x speed
CONTINUOUS_UPDATE_INTERVAL = 100  # milliseconds base update rate
CONTINUOUS_PAN_STEP = 0.5  # seconds to jump when using pan buttons

# ICU Monitor parameters
ICU_WINDOW_DURATION = 6  # seconds visible on screen
ICU_UPDATE_INTERVAL = 100  # milliseconds (10 fps for smooth scrolling)
ICU_SCROLL_STEP = 10  # samples to advance per update (0.1 seconds at 100 Hz)

# XOR Time Chunks parameters
XOR_CHUNKS_DEFAULT_PERIOD = 5.0  # seconds per chunk (default)
XOR_CHUNKS_MIN_PERIOD = 0.2  # minimum chunk period
XOR_CHUNKS_MAX_PERIOD = 5.0  # maximum chunk period
XOR_CHUNKS_DEFAULT_DURATION = 10.0  # total duration to analyze (seconds)
XOR_CHUNKS_ALPHA = 0.7  # transparency for overlaid chunks
XOR_CHUNKS_THRESHOLD = 0.05  # mV - threshold for XOR erasure

# Polar Graph parameters
POLAR_DEFAULT_WINDOW = 5.0  # seconds to display
POLAR_MIN_WINDOW = 1.0  # minimum window
POLAR_MAX_WINDOW = 20.0  # maximum window
POLAR_CUMULATIVE_DEFAULT = False  # Start with latest mode (not cumulative)
POLAR_UPDATE_INTERVAL = 100  # milliseconds for live mode

# Phase Space Recurrence parameters
PHASE_SPACE_WINDOW_DURATION = 10  # seconds to analyze
PHASE_SPACE_GRID_RESOLUTION = 0.1  # mV - bin size for grouping similar points
PHASE_SPACE_MIN_COUNT_DISPLAY = 1  # Minimum occurrence count to display

# Colormap options for 2D plots
AVAILABLE_COLORMAPS = [
    'Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis',
    'Blues', 'Reds', 'Greens', 'Purples', 'Oranges',
    'Hot', 'Cool', 'Rainbow', 'Jet', 'Turbo',
    'Electric', 'Portland', 'Picnic'
]
DEFAULT_COLORMAP = 'Viridis'

# Model parameters
MODEL_INPUT_SIZE = 1000
DIAGNOSIS_LABELS = ['NORM', 'MI', 'STTC', 'CD', 'HYP']

# Visualization parameters
MAJOR_GRID_INTERVAL = 0.2  # 200ms
MINOR_GRID_INTERVAL = 0.04  # 40ms
MAX_RECURRENCE_SAMPLES = 500


# Default values
DEFAULT_LEAD_X = 0
DEFAULT_LEAD_Y = 1
DEFAULT_RECURRENCE_THRESHOLD = 0.1
DEFAULT_DOWNSAMPLE_FACTOR = 2
DEFAULT_SELECTED_CHANNELS = [0, 1]
DEFAULT_XOR_CHANNEL_1 = 0
DEFAULT_XOR_CHANNEL_2 = 1
DEFAULT_PHASE_SPACE_CHANNEL_1 = 0
DEFAULT_PHASE_SPACE_CHANNEL_2 = 11