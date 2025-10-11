# 🎵 Doppler Effect Analyzer
Simulates the Doppler effect in vehicle pass-by scenarios. Estimate vehicle speeds from audio recordings or create realistic simulations with customizable parameters.

## What It Does

**Detection Mode**: Upload a vehicle pass-by recording and the app will analyze the frequency shift to estimate the vehicle's speed and calculate the original sound frequency. Perfect for studying real-world Doppler effects.

**Generation Mode**: Create your own Doppler effect simulations. Watch an animated car drive past an observer while hearing the characteristic frequency shift in real-time stereo audio.

## Key Features

### For Detection
- Drag-and-drop audio file upload
- Integrated audio player with playback controls
- Visual waveform display
- Automatic speed estimation using neural network models
- Source frequency calculation from Doppler shift
- Support for 10 different vehicle types

### For Generation
- Real-time animated simulation
- Adjustable source frequency, vehicle speed, and lateral distance
- Live frequency tracking as the vehicle passes
- Stereo audio with spatial positioning
- Visual metrics dashboard

## How It Works

**Detection** extracts frequencies from your audio using spectrogram analysis, identifies the peak frequency at closest approach, then uses the trained model to predict speed. The inverse Doppler formula calculates what the original source frequency must have been.

**Generation** computes the vehicle's trajectory, calculates the observed frequency at each moment using Doppler equations, and synthesizes stereo audio with realistic spatial panning and distance-based attenuation.

## Technical Notes

- Assumes sound speed of 343 m/s
- Supports audio sampling at 44.1 kHz
- Analyzes frequencies between 300-1800 Hz
- Simulation runs from -200m to +200m with observer at center
- Uses equal-power panning law for stereo positioning
- Applies Savitzky-Golay filtering for smooth frequency curves

## Supported Vehicles

Citroen C4 Picasso • Mazda 3 • Mercedes AMG 550 • Nissan Qashqai • Opel Insignia • Peugeot 3008 • Peugeot 307 • Renault Captur • Renault Scenic • VW Passat

## Dependencies

Requires Dash, Dash Bootstrap Components, h5py, NumPy, SciPy, Werkzeug, and Plotly. The detection mode also needs the H5 model file containing pre-trained speed estimation data.

## Design Philosophy

Built with a modern, card-based interface featuring gradient headers and smooth animations. The UI emphasizes clarity and ease of use, making complex acoustic analysis accessible through intuitive controls and real-time visual feedback.
