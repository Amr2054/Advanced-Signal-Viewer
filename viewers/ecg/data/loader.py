"""
Data loading utilities for ECG Viewer
"""
from io import BytesIO

import numpy as np
from viewers.ecg.config import DATA_PATH,zip_path
import zipfile


class ECGDataLoader:
    """Handles loading and accessing ECG data from .npz files"""

    def __init__(self, data_path=DATA_PATH):
        """Load ECG data from specified path"""

        # with zipfile.ZipFile(zip_path, 'r') as archive:
        #     self.data = np.load(BytesIO(archive.read('data_2.npz')))

        self.data = np.load(data_path)
        self.X = self.data['X_test']  # Patient and sample metadata
        self.Y = self.data['Y_test_non_scaled']  # ECG curves (non-scaled)
        self.Z = self.data['Z_test']  # Targets
        self.Y_scaled = self.data['Y_test']  # Scaled ECG curves

    def get_record(self, record_index):
        """
        Get a specific ECG record

        Args:
            record_index (int): Index of the record to retrieve

        Returns:
            tuple: (metadata, signal, signal_scaled, target)
        """
        return (
            self.X[record_index],
            self.Y[record_index],
            self.Y_scaled[record_index],
            self.Z[record_index]
        )

    def get_num_records(self):
        """Get total number of records"""
        return self.X.shape[0]

    def get_num_leads(self):
        """Get number of leads in the ECG data"""
        return self.Y.shape[2]