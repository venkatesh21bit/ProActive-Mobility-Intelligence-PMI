"""
Feature Engineering Module
Extracts features from vehicle telemetry time-series data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class TelemetryFeatureExtractor:
    """
    Extracts statistical and domain-specific features from vehicle telemetry
    """
    
    def __init__(self, window_size: int = 20):
        """
        Args:
            window_size: Number of recent data points to use for rolling statistics
        """
        self.window_size = window_size
        
    def extract_rolling_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract rolling statistical features from telemetry data
        
        Args:
            data: DataFrame with telemetry data sorted by time
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Sensor columns to analyze
        sensor_cols = [
            'engine_temperature', 'coolant_temperature', 'oil_pressure',
            'vibration_level', 'rpm', 'speed', 'battery_voltage'
        ]
        
        for col in sensor_cols:
            if col not in data.columns:
                continue
                
            values = data[col].dropna()
            
            if len(values) == 0:
                continue
            
            # Basic statistics
            features[f'{col}_mean'] = values.mean()
            features[f'{col}_std'] = values.std()
            features[f'{col}_min'] = values.min()
            features[f'{col}_max'] = values.max()
            features[f'{col}_median'] = values.median()
            
            # Range and variance
            features[f'{col}_range'] = values.max() - values.min()
            features[f'{col}_variance'] = values.var()
            
            # Percentiles
            features[f'{col}_p25'] = values.quantile(0.25)
            features[f'{col}_p75'] = values.quantile(0.75)
            
            # Trend (slope of linear regression)
            if len(values) > 1:
                x = np.arange(len(values))
                slope, _, _, _, _ = stats.linregress(x, values)
                features[f'{col}_trend'] = slope
            
            # Recent vs historical comparison
            if len(values) >= self.window_size:
                recent = values.tail(self.window_size // 2)
                historical = values.head(self.window_size // 2)
                features[f'{col}_recent_vs_historical'] = recent.mean() - historical.mean()
        
        return features
    
    def extract_domain_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract domain-specific automotive features
        
        Args:
            data: DataFrame with telemetry data
            
        Returns:
            Dictionary of domain features
        """
        features = {}
        
        # Engine health indicators
        if 'engine_temperature' in data.columns and 'coolant_temperature' in data.columns:
            temp_diff = data['engine_temperature'] - data['coolant_temperature']
            features['temp_differential_mean'] = temp_diff.mean()
            features['temp_differential_std'] = temp_diff.std()
            
            # Overheating events
            features['overheating_count'] = (data['engine_temperature'] > 105).sum()
            features['overheating_ratio'] = features['overheating_count'] / len(data)
        
        # Oil pressure issues
        if 'oil_pressure' in data.columns:
            features['low_oil_pressure_count'] = (data['oil_pressure'] < 25).sum()
            features['low_oil_pressure_ratio'] = features['low_oil_pressure_count'] / len(data)
        
        # Vibration anomalies
        if 'vibration_level' in data.columns:
            features['high_vibration_count'] = (data['vibration_level'] > 2.0).sum()
            features['high_vibration_ratio'] = features['high_vibration_count'] / len(data)
        
        # RPM patterns
        if 'rpm' in data.columns:
            features['high_rpm_count'] = (data['rpm'] > 3000).sum()
            features['rpm_variation'] = data['rpm'].std() / (data['rpm'].mean() + 1e-6)
        
        # Battery health
        if 'battery_voltage' in data.columns:
            features['low_battery_count'] = (data['battery_voltage'] < 12.0).sum()
            features['battery_health_score'] = data['battery_voltage'].mean() / 12.6
        
        # Speed patterns
        if 'speed' in data.columns:
            features['avg_speed'] = data['speed'].mean()
            features['max_speed'] = data['speed'].max()
            features['speed_changes'] = data['speed'].diff().abs().sum()
        
        # Fuel consumption estimate (if fuel_level available)
        if 'fuel_level' in data.columns:
            fuel_drop = data['fuel_level'].iloc[0] - data['fuel_level'].iloc[-1]
            features['fuel_consumption_rate'] = fuel_drop / len(data) if len(data) > 0 else 0
        
        return features
    
    def extract_time_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract time-based features
        
        Args:
            data: DataFrame with 'time' column
            
        Returns:
            Dictionary of time features
        """
        features = {}
        
        if 'time' not in data.columns or len(data) == 0:
            return features
        
        # Time span
        time_span = (data['time'].max() - data['time'].min()).total_seconds()
        features['time_span_seconds'] = time_span
        
        # Data frequency
        features['data_point_count'] = len(data)
        features['avg_sampling_interval'] = time_span / max(len(data) - 1, 1)
        
        return features
    
    def extract_all_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract all feature types
        
        Args:
            data: DataFrame with telemetry data
            
        Returns:
            Dictionary of all extracted features
        """
        features = {}
        
        # Extract different feature types
        features.update(self.extract_rolling_features(data))
        features.update(self.extract_domain_features(data))
        features.update(self.extract_time_features(data))
        
        # Replace NaN/Inf with 0
        features = {k: (0.0 if not np.isfinite(v) else float(v)) 
                   for k, v in features.items()}
        
        logger.debug(f"Extracted {len(features)} features")
        
        return features
    
    def get_feature_vector(self, features: Dict[str, float], feature_names: List[str]) -> np.ndarray:
        """
        Convert feature dictionary to ordered numpy array
        
        Args:
            features: Dictionary of features
            feature_names: List of expected feature names in order
            
        Returns:
            Numpy array of feature values
        """
        return np.array([features.get(name, 0.0) for name in feature_names])
