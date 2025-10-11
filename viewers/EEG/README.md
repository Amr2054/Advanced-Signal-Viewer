# EEG Signal Viewer - Dynamic Analysis

A web-based application for EEG signal visualization with automated seizure detection using deep learning.

## Project Structure

```
EEG-Signal-Viewer/
│
├── viewers/
│   └── EEG/
│       ├── __init__.py
│       ├── Data_helper.py              # Data loading and CNN model inference
│       ├── visualize_utils.py          # Visualization generators
│       │
│       ├── callbacks/
│       │   ├── __init__.py
│       │   └── app_callbacks.py        # Interactive callbacks
│       │
│       ├── layout/
│       │   ├── __init__.py
│       │   └── app_layout.py           # Dashboard layout
│       │
│       ├── config/
│       │   └── config.yaml             # Configuration file
│       │
│       └── Model/
│           └── CHB_MIT_sz_detec_demo.h5  # Trained CNN model
│
└── README.md
```

## Core Components

### DataManager (`Data_helper.py`)
Handles EEG data processing and seizure detection:
- Loads EDF files and validates channel labels
- Segments signals into fixed-size windows (default: 23040 samples)
- Applies CNN model to each segment for seizure probability prediction
- Threshold: probability > 0.5 indicates seizure

### PlotGenerator (`visualize_utils.py`)
Generates five visualization types:

**1. Summary Plot**
- Bar chart showing seizure probability for all segments
- Color-coded: red (seizure) vs green (normal)

**2. Continuous Viewer**
- Displays signal in time windows with playback control
- Dual view: Amplitude-Time and Polar plots
- Adjustable window size and playback speed

**3. Segment Plots**
- Detailed view of individual segments
- Shows seizure probability and classification

**4. Cross Recurrence Plot (CRP)**
- Visualizes recurrence patterns between two channels
- Uses scatter plot with color intensity showing occurrence frequency

**5. XOR Graph**
- Compares signal chunks using difference operation
- Applies threshold filtering to highlight significant changes
- Overlays multiple chunks for pattern analysis

## Installation

```bash
pip install numpy tensorflow keras mne plotly dash pyyaml
```

## Configuration

Key parameters in `config.yaml`:

```yaml
DOWNSAMPLING_FACTOR: 4           # For CNN model input
SFREQ: 256                       # Sampling frequency
SEGMENT_SIZE: 23040              # Samples per segment
CH_LABELS: [...]                 # Expected EEG channel names
```

## Usage

1. **Prepare Data**: Package EDF file in ZIP format
2. **Upload**: Drag and drop ZIP file into the application
3. **Analysis**: Automatic segmentation and seizure detection runs
4. **Visualize**: Explore results using interactive plots

## Model Details

- **Architecture**: Convolutional Neural Network
- **Input**: 18-channel EEG segments (downsampled)
- **Output**: Seizure probability (0-1)
- **Training**: CHB-MIT Scalp EEG Database

## Key Features

- **Automated Detection**: CNN-based seizure classification for each segment
- **Real-time Playback**: Stream through signals with variable speed
- **Multi-channel Analysis**: Compare relationships between channels
- **Interactive Controls**: Dynamic parameter adjustment for all visualizations