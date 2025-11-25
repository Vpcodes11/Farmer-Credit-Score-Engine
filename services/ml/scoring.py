"""
Deterministic scoring function for Farmer Credit Score Engine
Provides transparent, rule-based scoring as fallback to ML model
"""
from typing import Dict, List, Tuple
from .features import extract_features, FEATURE_WEIGHTS, get_feature_descriptions

def compute_deterministic_score(farmer_data: Dict) -> Tuple[float, List[Dict]]:
    """
    Compute farmer credit score using deterministic weighted sum
    
    Args:
        farmer_data: Dictionary containing farmer information
    
    Returns:
        Tuple of (score, drivers) where:
        - score: Credit score from 0 to 100
        - drivers: List of top 3 feature impacts with explanations
    """
    # Extract and normalize features
    features = extract_features(farmer_data)
    
    # Compute weighted score
    weighted_contributions = {}
    total_score = 0.0
    
    for feature_name, weight in FEATURE_WEIGHTS.items():
        feature_value = features.get(feature_name, 0.5)
        contribution = feature_value * weight * 100
        weighted_contributions[feature_name] = contribution
        total_score += contribution
    
    # Ensure score is in valid range
    score = max(0.0, min(100.0, total_score))
    
    # Generate drivers (top 3 features by absolute deviation from neutral)
    drivers = generate_drivers(features, weighted_contributions, farmer_data)
    
    return round(score, 1), drivers

def generate_drivers(
    features: Dict[str, float],
    contributions: Dict[str, float],
    farmer_data: Dict
) -> List[Dict]:
    """
    Generate top 3 score drivers with human-readable explanations
    
    Args:
        features: Normalized feature values
        contributions: Weighted contributions to score
        farmer_data: Raw farmer data for context
    
    Returns:
        List of driver dictionaries with feature, impact, and explanation
    """
    feature_descriptions = get_feature_descriptions()
    
    # Calculate impact as deviation from neutral (50% contribution)
    impacts = []
    for feature_name, contribution in contributions.items():
        weight = FEATURE_WEIGHTS[feature_name]
        neutral_contribution = 0.5 * weight * 100
        impact = contribution - neutral_contribution
        
        impacts.append({
            'feature': feature_name,
            'impact': round(impact, 1),
            'contribution': round(contribution, 1),
            'normalized_value': features[feature_name]
        })
    
    # Sort by absolute impact
    impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
    
    # Get top 3 and add explanations
    drivers = []
    for impact_data in impacts[:3]:
        feature = impact_data['feature']
        impact = impact_data['impact']
        
        explanation = generate_explanation(
            feature,
            impact,
            impact_data['normalized_value'],
            farmer_data
        )
        
        drivers.append({
            'feature': feature_descriptions.get(feature, feature),
            'impact': impact,
            'explanation': explanation
        })
    
    return drivers

def generate_explanation(
    feature: str,
    impact: float,
    normalized_value: float,
    farmer_data: Dict
) -> str:
    """
    Generate human-readable explanation for a feature's impact
    
    Args:
        feature: Feature name
        impact: Impact on score (positive or negative)
        normalized_value: Normalized feature value (0-1)
        farmer_data: Raw farmer data
    
    Returns:
        Human-readable explanation string
    """
    explanations = {
        'ndvi_mean': {
            'positive': 'Strong crop health observed from satellite',
            'negative': 'Lower crop vigor detected from satellite'
        },
        'ndvi_trend': {
            'positive': 'Improving crop health trend',
            'negative': 'Declining crop vigor vs last season'
        },
        'rainfall_anomaly_3mo': {
            'positive': 'Favorable rainfall pattern',
            'negative': f"{'Excess' if farmer_data.get('rainfall_anomaly_3mo', 0) > 0 else 'Delayed'} rainfall observed"
        },
        'past_kcc_defaults': {
            'positive': 'Clean credit history',
            'negative': f"{int(farmer_data.get('past_kcc_defaults', 0))} default(s) in KCC history"
        },
        'upi_txn_freq': {
            'positive': 'Active digital transaction history',
            'negative': 'Limited digital payment activity'
        },
        'land_area': {
            'positive': 'Larger farm size',
            'negative': 'Smaller farm size'
        },
        'last_year_yield_est': {
            'positive': 'Strong previous yield',
            'negative': 'Lower yield in previous season'
        },
        'market_price_volatility': {
            'positive': 'Stable crop prices',
            'negative': 'High price volatility for crop'
        },
        'fpo_membership_flag': {
            'positive': 'Member of Farmer Producer Organization',
            'negative': 'Not part of FPO network'
        },
        'distance_to_mandi_km': {
            'positive': 'Close to market',
            'negative': f"Far from mandi ({round(farmer_data.get('distance_to_mandi_km', 0), 1)} km)"
        },
        'crop_type': {
            'positive': f"Growing {farmer_data.get('crop_type', 'crop')}",
            'negative': f"Growing {farmer_data.get('crop_type', 'crop')}"
        }
    }
    
    if feature in explanations:
        return explanations[feature]['positive' if impact >= 0 else 'negative']
    
    return f"{'Positive' if impact >= 0 else 'Negative'} contribution from {feature}"
