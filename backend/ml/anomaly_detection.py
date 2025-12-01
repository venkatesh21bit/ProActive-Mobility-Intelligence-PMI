"""
Anomaly Detection Models
Ensemble of Isolation Forest and XGBoost for failure prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple, Optional, List
import pickle
import joblib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AnomalyDetectionEnsemble:
    """
    Ensemble model combining Isolation Forest and XGBoost for anomaly detection
    """
    
    def __init__(
        self,
        isolation_forest_contamination: float = 0.1,
        xgb_params: Optional[Dict] = None
    ):
        """
        Args:
            isolation_forest_contamination: Expected proportion of outliers
            xgb_params: XGBoost parameters
        """
        self.scaler = StandardScaler()
        
        # Isolation Forest for unsupervised anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=isolation_forest_contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        
        # XGBoost for supervised classification (when labels available)
        default_xgb_params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss'
        }
        if xgb_params:
            default_xgb_params.update(xgb_params)
        
        self.xgboost = xgb.XGBClassifier(**default_xgb_params)
        
        self.feature_names: List[str] = []
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None, feature_names: Optional[List[str]] = None):
        """
        Train the ensemble model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (optional, for XGBoost supervision)
            feature_names: List of feature names
        """
        logger.info(f"Training anomaly detection ensemble on {X.shape[0]} samples with {X.shape[1]} features")
        
        if feature_names:
            self.feature_names = feature_names
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest (unsupervised)
        self.isolation_forest.fit(X_scaled)
        logger.info("Isolation Forest trained")
        
        # Train XGBoost if labels provided
        if y is not None:
            self.xgboost.fit(X_scaled, y)
            logger.info("XGBoost trained")
        
        self.is_fitted = True
        
    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomaly scores (higher = more anomalous)
        
        Args:
            X: Feature matrix
            
        Returns:
            Anomaly scores (0-1, where 1 = high anomaly)
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        
        X_scaled = self.scaler.transform(X)
        
        # Isolation Forest scores (-1 to 1, we convert to 0-1)
        if_scores = self.isolation_forest.score_samples(X_scaled)
        if_scores_normalized = (1 - (if_scores - if_scores.min()) / (if_scores.max() - if_scores.min() + 1e-6))
        
        return if_scores_normalized
    
    def predict_failure_probability(self, X: np.ndarray) -> np.ndarray:
        """
        Predict failure probability using XGBoost
        
        Args:
            X: Feature matrix
            
        Returns:
            Failure probabilities (0-1)
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        
        X_scaled = self.scaler.transform(X)
        
        try:
            probabilities = self.xgboost.predict_proba(X_scaled)[:, 1]
            return probabilities
        except Exception as e:
            logger.warning(f"XGBoost prediction failed: {e}, using Isolation Forest only")
            return self.predict_anomaly_score(X)
    
    def predict(self, X: np.ndarray, ensemble_weight: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict using ensemble (combines both models)
        
        Args:
            X: Feature matrix
            ensemble_weight: Weight for XGBoost (0-1), remainder for Isolation Forest
            
        Returns:
            Tuple of (ensemble_scores, anomaly_scores, failure_probabilities)
        """
        anomaly_scores = self.predict_anomaly_score(X)
        failure_probs = self.predict_failure_probability(X)
        
        # Ensemble: weighted average
        ensemble_scores = (ensemble_weight * failure_probs + 
                          (1 - ensemble_weight) * anomaly_scores)
        
        return ensemble_scores, anomaly_scores, failure_probs
    
    def get_feature_importance(self, top_n: int = 20) -> Dict[str, float]:
        """
        Get feature importance from XGBoost
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            Dictionary of feature importances
        """
        if not self.is_fitted or not self.feature_names:
            return {}
        
        try:
            importance = self.xgboost.feature_importances_
            feature_importance = dict(zip(self.feature_names, importance))
            
            # Sort and get top N
            sorted_importance = dict(sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n])
            
            return sorted_importance
        except Exception as e:
            logger.warning(f"Could not get feature importance: {e}")
            return {}
    
    def save(self, path: Path):
        """Save model to disk"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save components
        joblib.dump(self.scaler, path / 'scaler.pkl')
        joblib.dump(self.isolation_forest, path / 'isolation_forest.pkl')
        joblib.dump(self.xgboost, path / 'xgboost.pkl')
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted
        }
        with open(path / 'metadata.pkl', 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path):
        """Load model from disk"""
        path = Path(path)
        
        self.scaler = joblib.load(path / 'scaler.pkl')
        self.isolation_forest = joblib.load(path / 'isolation_forest.pkl')
        self.xgboost = joblib.load(path / 'xgboost.pkl')
        
        with open(path / 'metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        
        self.feature_names = metadata['feature_names']
        self.is_fitted = metadata['is_fitted']
        
        logger.info(f"Model loaded from {path}")


class FailurePredictor:
    """
    High-level failure prediction with severity classification
    """
    
    def __init__(self, model: AnomalyDetectionEnsemble):
        self.model = model
        
        # Severity thresholds
        self.severity_thresholds = {
            'critical': 0.8,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.2
        }
    
    def classify_severity(self, score: float) -> str:
        """Classify failure severity based on score"""
        if score >= self.severity_thresholds['critical']:
            return 'critical'
        elif score >= self.severity_thresholds['high']:
            return 'high'
        elif score >= self.severity_thresholds['medium']:
            return 'medium'
        elif score >= self.severity_thresholds['low']:
            return 'low'
        else:
            return 'normal'
    
    def predict_with_explanation(self, features: Dict[str, float]) -> Dict:
        """
        Predict failure with detailed explanation
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Prediction dictionary with score, severity, and explanation
        """
        # Convert features to array
        feature_vector = np.array([features.get(name, 0.0) 
                                   for name in self.model.feature_names]).reshape(1, -1)
        
        # Get predictions
        ensemble_score, anomaly_score, failure_prob = self.model.predict(feature_vector)
        
        score = float(ensemble_score[0])
        severity = self.classify_severity(score)
        
        # Get feature importance for explanation
        feature_importance = self.model.get_feature_importance(top_n=5)
        
        # Build explanation
        explanation = self._build_explanation(features, feature_importance, severity)
        
        return {
            'failure_probability': float(failure_prob[0]),
            'anomaly_score': float(anomaly_score[0]),
            'ensemble_score': score,
            'severity': severity,
            'confidence': min(abs(score - 0.5) * 2, 1.0),  # Distance from decision boundary
            'feature_importance': feature_importance,
            'explanation': explanation
        }
    
    def _build_explanation(
        self,
        features: Dict[str, float],
        importance: Dict[str, float],
        severity: str
    ) -> str:
        """Build human-readable explanation"""
        if severity == 'normal':
            return "Vehicle operating normally with no significant anomalies detected."
        
        explanations = []
        
        # Check for specific issues based on top important features
        for feature_name, importance_score in list(importance.items())[:3]:
            value = features.get(feature_name, 0.0)
            
            if 'engine_temperature' in feature_name and value > 100:
                explanations.append(f"High engine temperature detected ({value:.1f}°C)")
            elif 'oil_pressure' in feature_name and value < 30:
                explanations.append(f"Low oil pressure detected ({value:.1f} PSI)")
            elif 'vibration' in feature_name and value > 2.0:
                explanations.append(f"Excessive vibration detected ({value:.2f}g)")
            elif 'battery' in feature_name and value < 12.0:
                explanations.append(f"Low battery voltage ({value:.1f}V)")
        
        if explanations:
            return "; ".join(explanations)
        else:
            return f"Multiple anomalies detected indicating {severity} severity failure risk."
