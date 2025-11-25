"""
Feature engineering utilities for Farmer Credit Score Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List

# Feature definitions and weights for deterministic scoring
FEATURE_WEIGHTS = {
    'land_area': 0.08,
    'crop_type': 0.06,
    'last_year_yield_est': 0.12,
    'ndvi_mean': 0.15,
    'ndvi_trend': 0.10,
    'rainfall_anomaly_3mo': 0.08,
    'past_kcc_defaults': 0.15,
    'upi_txn_freq': 0.10,
    'market_price_volatility': 0.06,
    'fpo_membership_flag': 0.05,
    'distance_to_mandi_km': 0.05
}

# Crop type encoding
CROP_ENCODING = {
    'rice': 0.8,
    'wheat': 0.9,
    'cotton': 0.7,
    'maize': 0.75
}

def normalize_feature(value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
    """
    Normalize a feature value to 0-1 range
    
    Args:
        value: Raw feature value
        min_val: Minimum expected value
        max_val: Maximum expected value
        inverse: If True, higher values result in lower scores
    
    Returns:
        Normalized value between 0 and 1
    """
    if max_val == min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0.0, min(1.0, normalized))
    
    if inverse:
        normalized = 1.0 - normalized
    
    return normalized

def extract_features(farmer_data: Dict) -> Dict[str, float]:
    """
    Extract and normalize features from farmer data
    
    Args:
        farmer_data: Dictionary containing farmer information
    
    Returns:
        Dictionary of normalized features
    """
    features = {}
    
    # Land area (0.5 to 10 hectares)
    features['land_area'] = normalize_feature(
        farmer_data.get('land_area', 2.0), 0.5, 10.0
    )
    
    # Crop type (encoded)
    crop_type = farmer_data.get('crop_type', 'rice')
    features['crop_type'] = CROP_ENCODING.get(crop_type, 0.7)
    
    # Last year yield estimate (normalized per hectare)
    land_area = farmer_data.get('land_area', 2.0)
    yield_est = farmer_data.get('last_year_yield_est', 3.0)
    yield_per_hectare = yield_est / land_area if land_area > 0 else 0
    features['last_year_yield_est'] = normalize_feature(
        yield_per_hectare, 1.5, 5.0
    )
    
    # NDVI mean (0.2 to 0.9)
    features['ndvi_mean'] = normalize_feature(
        farmer_data.get('ndvi_mean', 0.5), 0.2, 0.9
    )
    
    # NDVI trend (-0.15 to +0.15)
    features['ndvi_trend'] = normalize_feature(
        farmer_data.get('ndvi_trend', 0.0), -0.15, 0.15
    )
    
    # Rainfall anomaly (-50 to +50 mm, optimal is near 0)
    rainfall_anomaly = farmer_data.get('rainfall_anomaly_3mo', 0.0)
    # Convert to deviation from optimal (0)
    features['rainfall_anomaly_3mo'] = 1.0 - normalize_feature(
        abs(rainfall_anomaly), 0, 50
    )
    
    # Past KCC defaults (0 to 3+, inverse)
    defaults = farmer_data.get('past_kcc_defaults', 0)
    features['past_kcc_defaults'] = normalize_feature(
        defaults, 0, 3, inverse=True
    )
    
    # UPI transaction frequency (0 to 50 per month)
    features['upi_txn_freq'] = normalize_feature(
        farmer_data.get('upi_txn_freq', 10), 0, 50
    )
    
    # Market price volatility (5% to 30%, inverse)
    features['market_price_volatility'] = normalize_feature(
        farmer_data.get('market_price_volatility', 15), 5, 30, inverse=True
    )
    
    # FPO membership (binary)
    features['fpo_membership_flag'] = float(
        farmer_data.get('fpo_membership_flag', 0)
    )
    
    # Distance to mandi (2 to 50 km, inverse)
    features['distance_to_mandi_km'] = normalize_feature(
        farmer_data.get('distance_to_mandi_km', 20), 2, 50, inverse=True
    )
    
    return features

def get_feature_names() -> List[str]:
    """Get list of all feature names"""
    return list(FEATURE_WEIGHTS.keys())

def get_feature_descriptions() -> Dict[str, str]:
    """Get human-readable descriptions for each feature"""
    return {
        'land_area': 'Farm size',
        'crop_type': 'Crop category',
        'last_year_yield_est': 'Previous yield',
        'ndvi_mean': 'Crop health (satellite)',
        'ndvi_trend': 'Crop vigor trend',
        'rainfall_anomaly_3mo': 'Rainfall pattern',
        'past_kcc_defaults': 'Credit history',
        'upi_txn_freq': 'Digital transactions',
        'market_price_volatility': 'Price stability',
        'fpo_membership_flag': 'FPO membership',
        'distance_to_mandi_km': 'Market access'
    }
