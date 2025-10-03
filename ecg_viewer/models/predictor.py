"""
Model loading and prediction utilities
"""
import numpy as np
from tensorflow.keras.models import load_model
from config import MODEL_PATH, MODEL_INPUT_SIZE, DIAGNOSIS_LABELS


class ECGPredictor:
    """Handles ECG diagnosis prediction using trained model"""

    def __init__(self, model_path=MODEL_PATH):
        """Load the trained model"""
        self.model = load_model(model_path)
        self.labels = DIAGNOSIS_LABELS

    def predict(self, metadata, signal_scaled):
        """
        Predict diagnosis from ECG signal

        Args:
            metadata (np.ndarray): Patient metadata (X_test)
            signal_scaled (np.ndarray): Scaled ECG signal

        Returns:
            dict: Prediction results containing label and confidence
        """
        try:
            # Prepare signal for prediction
            signal_for_pred = self._prepare_signal(signal_scaled)

            # Prepare inputs
            X_test = np.expand_dims(metadata, axis=0)
            Y_test = np.expand_dims(signal_for_pred, axis=0)

            # Get predictions
            predictions = self.model.predict([X_test, Y_test])
            pred_index = np.argmax(predictions, axis=1)[0]
            pred_label = self.labels[pred_index]
            confidence = np.max(predictions)

            return {
                'label': pred_label,
                'confidence': confidence,
                'success': True,
                'error': None
            }

        except Exception as e:
            return {
                'label': None,
                'confidence': None,
                'success': False,
                'error': str(e)
            }

    def _prepare_signal(self, signal_scaled):
        """
        Prepare signal for model input (pad or truncate to MODEL_INPUT_SIZE)

        Args:
            signal_scaled (np.ndarray): Scaled ECG signal

        Returns:
            np.ndarray: Prepared signal of shape (MODEL_INPUT_SIZE, num_leads)
        """
        if signal_scaled.shape[0] > MODEL_INPUT_SIZE:
            return signal_scaled[:MODEL_INPUT_SIZE, :]
        elif signal_scaled.shape[0] < MODEL_INPUT_SIZE:
            pad_len = MODEL_INPUT_SIZE - signal_scaled.shape[0]
            return np.pad(signal_scaled, ((0, pad_len), (0, 0)), mode="constant")
        else:
            return signal_scaled