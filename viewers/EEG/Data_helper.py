import numpy as np
import logging
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from keras.models import load_model
import yaml
import mne
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path (change on your device)
Path = 'viewers/EEG/'

# -------- Load Configs --------
with open(f"{Path}config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# -----------------------
# Constants
# -----------------------
DOWNSAMPLING_FACTOR = config['DOWNSAMPLING_FACTOR']
SFREQ = config['SFREQ']
CH_LABELS = config['CH_LABELS']
SEGMENT_SIZE = config['SEGMENT_SIZE']


# -----------------------
# Data Manager Class
# -----------------------
class DataManager:
    """Manages EEG data loading and preprocessing."""

    def __init__(self, edf_file):
        self.edf_file = edf_file
        self.segments = []
        self.segment_predictions = []
        self.load_data()
        self.load_model()
        self.process_segments()

    def load_data(self, ch_labels=CH_LABELS, verbose=True):
        logger.info("Loading data files...")
        if verbose:
            print(f'{self.edf_file}: Reading.')

        # load EDF file
        self.temp_edf = mne.io.read_raw_edf(self.edf_file, preload=True, verbose="ERROR")

        if sum([any([0 if re.match(c, l) == None else 1 for l in self.temp_edf.ch_names]) for c in ch_labels]) == len(
                ch_labels):
            ch_mapping = {sorted([l for l in self.temp_edf.ch_names if re.match(c, l) != None])[0]: c for c in
                          ch_labels}
            self.temp_edf.rename_channels(ch_mapping)
            self.temp_edf = self.temp_edf.pick(ch_labels)

            self.temp_signals = self.temp_edf.get_data(picks=ch_labels) * 1e6
            self.total_samples = self.temp_signals.shape[1]

            # Calculate how many complete segments we can extract
            self.n_segments = self.total_samples // SEGMENT_SIZE

            # Store original sampling frequency
            self.original_sfreq = int(1 / (self.temp_edf.times[1] - self.temp_edf.times[0]))

            # Create time axis for the entire signal
            self.time_axis = np.arange(self.total_samples) / self.original_sfreq

            logger.info(f"Data loaded. Total samples: {self.total_samples}, Segments: {self.n_segments}")
        else:
            if verbose == True:
                print('EEG {}: Not appropriate channel labels. Reading skipped.'.format(self.edf_file))

    def load_model(self):
        """Load the Keras model once."""
        logger.info("Loading model...")
        self.model = load_model(f'{Path}Model/CHB_MIT_sz_detec_demo.h5')
        logger.info("Model loaded successfully")

    def process_segments(self):
        """Process all segments and run predictions."""
        logger.info(f"Processing {self.n_segments} segments...")

        for seg_idx in range(self.n_segments):
            start_idx = seg_idx * SEGMENT_SIZE
            end_idx = start_idx + SEGMENT_SIZE

            # Extract segment
            segment_data = self.temp_signals[:, start_idx:end_idx]

            # Prepare for CNN (with downsampling for model)
            segment_downsampled = segment_data[:, ::DOWNSAMPLING_FACTOR]
            segment_cnn = segment_downsampled[:, :, np.newaxis]

            # Run prediction
            pred = self.model.predict(segment_cnn[np.newaxis, :, :, :], verbose=0)[0][0]

            # Store segment info
            self.segments.append({
                'index': seg_idx,
                'start_sample': start_idx,
                'end_sample': end_idx,
                'start_time': start_idx / self.original_sfreq,
                'end_time': end_idx / self.original_sfreq,
                'data': segment_data
            })

            self.segment_predictions.append({
                'segment': seg_idx,
                'prediction': pred,
                'is_seizure': pred > 0.5
            })

            if pred > 0.5:
                logger.info(f"Seizure detected in segment {seg_idx} (prob: {pred:.3f})")
            else:
                logger.info(f"Segment {seg_idx} is Normal (prob: {pred:.3f})")