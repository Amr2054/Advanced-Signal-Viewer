from io import BytesIO
import numpy as np
from viewers.ecg.config import DATA_PATH, zip_path
import zipfile
import os


class ECGDataLoader:
    """Handles loading and accessing ECG data from .npz files"""

    def __init__(self, data_path=DATA_PATH):
        """Load ECG data from specified path"""
        self.data = None
        self.data_path = data_path
        self.original_data_path = data_path  # Store original path
        self.load_data(data_path)

    def load_data(self, data_path):
        """Load data from a given path"""
        try:
            self.data = np.load(data_path)
            self.data_path = data_path
            self.X = self.data['X_test']  # Patient and sample metadata
            self.Y = self.data['Y_test_non_scaled']  # ECG curves (non-scaled)
            self.Z = self.data['Z_test']  # Targets
            self.Y_scaled = self.data['Y_test']  # Scaled ECG curves
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def reload_original(self):
        """Reload the original preloaded data"""
        return self.load_data(self.original_data_path)

    def load_from_zip(self, zip_file_path):
        """Load data from uploaded zip file containing .npz"""
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as archive:
                # Find .npz file in zip
                npz_files = [f for f in archive.namelist() if f.endswith('.npz')]
                if not npz_files:
                    return False, "No .npz file found in zip"

                # Load first .npz file found
                self.data = np.load(BytesIO(archive.read(npz_files[0])))
                self.X = self.data['X_test']
                self.Y = self.data['Y_test_non_scaled']
                self.Z = self.data['Z_test']
                self.Y_scaled = self.data['Y_test']
                return True, f"Loaded {npz_files[0]}"
        except Exception as e:
            return False, f"Error loading zip: {str(e)}"

    def load_from_npz(self, npz_file_path):
        """Load data from uploaded .npz file"""
        try:
            self.data = np.load(npz_file_path)
            self.X = self.data['X_test']
            self.Y = self.data['Y_test_non_scaled']
            self.Z = self.data['Z_test']
            self.Y_scaled = self.data['Y_test']
            return True, "Data loaded successfully"
        except Exception as e:
            return False, f"Error loading npz: {str(e)}"

    def get_record(self, record_index):
        """
        Get a specific ECG record

        Args:
            record_index (int): Index of the record to retrieve

        Returns:
            tuple: (metadata, signal, signal_scaled, target)
        """
        if self.data is None:
            raise ValueError("No data loaded")

        return (
            self.X[record_index],
            self.Y[record_index],
            self.Y_scaled[record_index],
            self.Z[record_index]
        )

    def get_num_records(self):
        """Get total number of records"""
        if self.data is None:
            return 0
        return self.X.shape[0]

    def get_num_leads(self):
        """Get number of leads in the ECG data"""
        if self.data is None:
            return 12
        return self.Y.shape[2]