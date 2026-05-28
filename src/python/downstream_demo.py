import numpy as np
from typing import Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import xgboost as xgb

class GestureClassifier:
    """
    Lightweight gesture classifier using sEMG + IMU features.
    Demonstrates the downstream task integration with PhysioStream-Engine.
    """

    def __init__(self, n_classes: int = 5):
        self.n_classes = n_classes
        # Use XGBoost for balance of speed and accuracy
        self.model = xgb.XGBClassifier(
            n_estimators=50,
            max_depth=5,
            learning_rate=0.1,
            objective='multi:softmax',
            num_class=n_classes,
            n_jobs=1  # Single-threaded for low latency
        )
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, verbose: bool = True):
        """
        Train classifier on feature vectors.

        Args:
            X: [n_samples x n_features] feature matrix
            y: [n_samples] labels
        """
        self.model.fit(X, y)
        self._is_fitted = True
        if verbose:
            print(f"GestureClassifier trained on {X.shape[0]} samples")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict gesture labels for feature vectors."""
        if not self._is_fitted:
            raise ValueError("Classifier must be fitted before prediction")
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """Return accuracy on labeled data."""
        preds = self.predict(X)
        return np.mean(preds == y)