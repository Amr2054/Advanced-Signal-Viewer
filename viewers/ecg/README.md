# ECG Signal Viewer

A comprehensive web-based ECG (Electrocardiogram) signal visualization and analysis tool built with Dash and Plotly. This viewer provides multiple visualization modes and interactive controls for analyzing 12-lead ECG data.

![ECG Viewer](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## Table of Contents

- [Features Overview](#features-overview)
- [Data Source Options](#data-source-options)
- [Visualization Modes](#visualization-modes)
- [Lead Selection](#lead-selection)
- [AI-Powered Diagnosis](#ai-powered-diagnosis)
- [Use Cases](#use-cases)
- [Output & Export](#output--export)
---

## Features Overview

### Core Capabilities

- **Multiple Visualization Modes**: 5 different viewing modes for comprehensive ECG analysis
- **12-Lead ECG Support**: Full support for standard 12-lead ECG (I, II, III, aVR, aVL, aVF, V1-V6)
- **Flexible Data Input**: Upload custom data files or use preloaded datasets
- **Real-time Playback**: Animated playback with adjustable speed controls
- **AI Diagnosis**: Machine learning-based automatic ECG diagnosis
- **Interactive Controls**: Zoom, pan, and navigate through ECG recordings
- **Export-Ready Plots**: High-quality Plotly graphs with full interactivity

---

##  Data Source Options

### 1. **Preloaded Data**
- Access pre-configured ECG datasets
- Instant loading with no file upload required
- Multiple records available for analysis

### 2. **File Upload**
- **Supported Formats**:
  - `.npz` files (NumPy compressed arrays)
  - `.zip` files containing `.npz` data
- **Required Data Structure**:
  - `X_test`: Patient and sample metadata
  - `Y_test`: Scaled ECG signals
  - `Y_test_non_scaled`: Non-scaled ECG signals
  - `Z_test`: Target labels/diagnoses
- **Upload Method**: Drag-and-drop or file browser
- **Real-time Feedback**: Upload status and record count displayed

---

## Visualization Modes

### 1. **Static Mode**

**Description**: Traditional multi-lead ECG strip display

**Features**:
- Displays selected leads in stacked format
- Fixed time window (configurable duration)
- Clear grid overlay for precise measurements
- Time-aligned view of all selected leads

**Best For**:
- Initial ECG review
- Print-ready views
- Standard clinical interpretation
- Rhythm analysis across multiple leads


---

### 2. **Continuous Mode**

**Description**: Dynamic scrolling ECG viewer with VCR-like controls

**Features**:
- Smooth horizontal scrolling through the entire recording
- Adjustable playback speed (0.1x - 5.0x)
- Variable zoom levels (1s - 30s windows)
- Pan left/right for manual navigation
- Real-time position indicator

**Controls**:
- **▶ Play/⏸ Pause**: Start/stop automatic scrolling
- **⏮ Reset**: Jump to beginning
- **◀ Pan Left**: Manual backward navigation
- **▶ Pan Right**: Manual forward navigation
- **Speed Slider**: 0.1x to 5.0x playback speed
- **Zoom Slider**: 1s to 30s viewing window
- **Position Slider**: Direct jump to any time point

**Best For**:
- Reviewing long recordings
- Finding specific events in the signal
- Teaching and demonstrations
- Detailed rhythm analysis

---

### 3. **XOR Chunks Mode**

**Description**: Advanced temporal analysis comparing consecutive time segments

**Features**:
- Divides signal into equal time chunks
- Compares consecutive chunks using XOR logic
- Highlights differences between adjacent segments
- Threshold-based difference detection

**How It Works**:
- Signal divided into chunks of specified period
- Each chunk compared with the next
- Differences above threshold are displayed
- Empty result = chunks match (periodic signal)

**Controls**:
- **Channel Selection**: Choose single lead to analyze
- **Chunk Period**: 0.2s - 5.0s (duration of each segment)
- **Threshold**: 0.01 - 0.5 mV (sensitivity for detecting differences)

**Best For**:
- Detecting rhythm irregularities
- Finding periodic patterns
- Identifying signal consistency
- Arrhythmia analysis

**Interpretation**:
- **Points shown**: Chunks differ (irregular rhythm)
- **Empty plot**: All chunks match (regular rhythm)

---

### 4. **Polar Mode**

**Description**: Circular representation mapping amplitude and time to polar coordinates

**Features**:
- **Dual View Display**:
  - **Top**: Polar graph (r = magnitude, θ = time)
  - **Bottom**: Synchronized time domain view
- **Two Display Modes**:
  - **Latest**: Shows only current window
  - **Cumulative**: Accumulates historical data with fading effect
- Animated playback with position tracking
- Color-coded magnitude visualization

**Polar Coordinates**:
- **r (radius)**: Absolute amplitude magnitude |signal|
- **θ (angle)**: Time mapped to 0° - 360°

**Controls**:
- **Channel Selection**: Single lead analysis
- **Window Size**: 1s - 20s viewing window
- **Display Mode**: Latest vs. Cumulative
- **▶ Play/⏸ Pause**: Animate through recording
- **⏮ Reset**: Clear cumulative data and restart

**Best For**:
- Visualizing signal periodicity
- Pattern recognition in circular space
- Educational demonstrations
- Alternative perspective on rhythm

**Unique Features**:
- Synchronized dual-view (polar + time domain)
- Real-time comparison between coordinate systems
- Visual pattern emergence in circular representation

---

### 5. **Cross Recurrence**

**Description**: 2D phase space recurrence plot comparing two leads

**Features**:
- Plots two leads against each other (X vs Y)
- Color-coded occurrence frequency
- Grid-based binning for pattern detection
- Multiple colormap options

**How It Works**:
- Each sample plotted as (Lead X, Lead Y) coordinate
- Points binned by amplitude resolution
- Color intensity = frequency of occurrence
- Reveals relationships between leads

**Controls**:
- **X-axis Lead**: First lead selection
- **Y-axis Lead**: Second lead selection
- **Resolution**: 0.01 - 0.5 mV (grid bin size)
- **Colormap**: 
  - Viridis (default)
  - Plasma
  - Turbo
  - And more...

**Best For**:
- Lead relationship analysis
- Detecting correlated patterns


**Interpretation**:
- **Tight clusters**: Strong correlation between leads
- **Scattered points**: Weak correlation
- **Diagonal patterns**: Similar signal characteristics
- **Color intensity**: Recurrence frequency

---

## Lead Selection

### Standard 12-Lead ECG

**Limb Leads** (Frontal Plane):
- **I**: Right arm to left arm
- **II**: Right arm to left leg
- **III**: Left arm to left leg
- **aVR**: Augmented vector right
- **aVL**: Augmented vector left
- **aVF**: Augmented vector foot

**Precordial Leads** (Horizontal Plane):
- **V1**: 4th intercostal space, right sternal border
- **V2**: 4th intercostal space, left sternal border
- **V3**: Between V2 and V4
- **V4**: 5th intercostal space, midclavicular line
- **V5**: Anterior axillary line, same level as V4
- **V6**: Midaxillary line, same level as V4

### Selection Options

- **Multi-select**: Choose any combination of leads
- **Visual Feedback**: Selected leads highlighted
- **Mode-specific**:
  - Static/Continuous: Multiple leads (stacked view)
  - XOR/Polar: Single lead analysis
  - Phase Space: Two leads (X and Y axes)

---

##  AI-Powered Diagnosis

### Automatic ECG Classification

**Features**:
- Deep learning-based diagnosis
- Trained on large ECG dataset
- Multi-class classification


**How to Use**:
1. Select a record
2. Click **🔬 Diagnose** button
3. View diagnosis output with label

**Output**:
- **Diagnosis Label**: Detected condition
- **Processing**: Uses scaled signal and metadata
- **Model**: Pre-trained CNN


**Note**: Results are for research/educational purposes. Not for clinical diagnosis.

---

## Use Cases

### Clinical Applications
- ECG review and interpretation
- Arrhythmia detection and analysis
- Comparative lead analysis

### Educational
- Teaching ECG interpretation
- Demonstrating cardiac rhythms
- Exploring signal processing concepts

### Research
- Algorithm development and testing
- Signal quality assessment
- Feature extraction validation
- Pattern recognition studies

---

## Output & Export

### Available Export Options:

- **PNG Images**: Click camera icon on any graph
---



## Acknowledgments

Built with:
- **Dash**: Web application framework
- **Plotly**: Interactive visualization library
- **NumPy**: Numerical computing
- **SciPy**: Signal processing
- **TensorFlow/Keras**: Deep learning models

---

## License

This project is licensed under the MIT License

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**Maintainer**: ECG Viewer Team
