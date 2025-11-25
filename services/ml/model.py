"""
ML Model wrapper with SHAP explainability for Farmer Credit Score Engine
"""
import os
import joblib
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor
    import shap
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn or shap not available. Using deterministic scoring only.")

from .features import extract_features, get_feature_names, get_feature_descriptions
from .scoring import compute_deterministic_score

class FarmerCreditModel:
    """
    Farmer Credit Score ML Model with SHAP explainability
    Falls back to deterministic scoring if model not available
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the model
        
        Args:
            model_path: Path to saved model file (.joblib)
        """
        self.model = None
        self.explainer = None
        self.feature_names = get_feature_names()
        self.feature_descriptions = get_feature_descriptions()
        
        if model_path and os.path.exists(model_path) and ML_AVAILABLE:
            try:
                self.model = joblib.load(model_path)
                # Initialize SHAP explainer
                self.explainer = shap.TreeExplainer(self.model)
                print(f"✓ Loaded ML model from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load model from {model_path}: {e}")
                print("Falling back to deterministic scoring")
    
    def predict(self, farmer_data: Dict) -> Tuple[float, List[Dict]]:
        """
        Predict credit score for a farmer
        
        Args:
            farmer_data: Dictionary containing farmer information
        
        Returns:
            Tuple of (score, drivers)
        """
        if self.model is None or not ML_AVAILABLE:
            # Use deterministic scoring as fallback
            return compute_deterministic_score(farmer_data)
        
        try:
            # Extract features
            features = extract_features(farmer_data)
            feature_vector = np.array([[features[name] for name in self.feature_names]])
            
            # Predict score
            score_normalized = self.model.predict(feature_vector)[0]
            score = max(0.0, min(100.0, score_normalized * 100))
            
            # Generate SHAP explanations
            drivers = self._generate_shap_drivers(feature_vector, farmer_data)
            
            return round(score, 1), drivers
            
        except Exception as e:
            print(f"Warning: ML prediction failed: {e}. Using deterministic scoring.")
            return compute_deterministic_score(farmer_data)
    
    def _generate_shap_drivers(
        self,
        feature_vector: np.ndarray,
        farmer_data: Dict
    ) -> List[Dict]:
        """
        Generate top 3 drivers using SHAP values
        
        Args:
            feature_vector: Normalized feature vector
            farmer_data: Raw farmer data
        
        Returns:
            List of driver dictionaries
        """
        if self.explainer is None:
            # Fallback to deterministic drivers
            _, drivers = compute_deterministic_score(farmer_data)
            return drivers
        
        try:
            # Compute SHAP values
            shap_values = self.explainer.shap_values(feature_vector)
            
            # Get feature impacts
            impacts = []
            for i, feature_name in enumerate(self.feature_names):
                shap_value = shap_values[0][i] * 100  # Scale to 0-100
                impacts.append({
                    'feature': feature_name,
                    'impact': shap_value,
                    'feature_value': feature_vector[0][i]
                })
            
            # Sort by absolute impact
            impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            # Generate top 3 drivers with explanations
            drivers = []
            for impact_data in impacts[:3]:
                feature = impact_data['feature']
                impact = impact_data['impact']
                
                explanation = self._generate_shap_explanation(
                    feature,
                    impact,
                    impact_data['feature_value'],
                    farmer_data
                )
                
                drivers.append({
                    'feature': self.feature_descriptions.get(feature, feature),
                    'impact': round(impact, 1),
                    'explanation': explanation
                })
            
            return drivers
            
        except Exception as e:
            print(f"Warning: SHAP explanation failed: {e}")
            _, drivers = compute_deterministic_score(farmer_data)
            return drivers
    
    def _generate_shap_explanation(
        self,
        feature: str,
        impact: float,
        normalized_value: float,
        farmer_data: Dict
    ) -> str:
        """Generate human-readable explanation for SHAP value"""
        # Use same explanation logic as deterministic scoring
        from .scoring import generate_explanation
        return generate_explanation(feature, impact, normalized_value, farmer_data)

# Global model instance
_model_instance = None

def get_model(model_path: Optional[str] = None) -> FarmerCreditModel:
    """
    Get or create global model instance
    
    Args:
        model_path: Path to model file
    
    Returns:
        FarmerCreditModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = FarmerCreditModel(model_path)
    return _model_instance
