"""
Model training script for Farmer Credit Score Engine
Trains RandomForest model on synthetic data and saves it
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from features import extract_features, get_feature_names
from scoring import compute_deterministic_score

def load_training_data(data_path: str = '../../sample_data/farmers.csv') -> pd.DataFrame:
    """Load synthetic farmer data"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, data_path)
    return pd.read_csv(full_path)

def prepare_features_and_labels(df: pd.DataFrame):
    """
    Prepare feature matrix and labels from farmer data
    
    Uses deterministic scoring as ground truth labels
    """
    feature_names = get_feature_names()
    X = []
    y = []
    
    for _, row in df.iterrows():
        farmer_data = row.to_dict()
        
        # Extract features
        features = extract_features(farmer_data)
        feature_vector = [features[name] for name in feature_names]
        X.append(feature_vector)
        
        # Use deterministic score as label (normalized to 0-1)
        score, _ = compute_deterministic_score(farmer_data)
        y.append(score / 100.0)
    
    return np.array(X), np.array(y), feature_names

def train_model(X, y, feature_names):
    """Train RandomForest model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train RandomForest
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    print("\nTraining RandomForest model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    print("\n" + "="*60)
    print("MODEL PERFORMANCE")
    print("="*60)
    print("\nTraining Set:")
    print(f"  R² Score: {r2_score(y_train, y_pred_train):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_train, y_pred_train)):.4f}")
    print(f"  MAE: {mean_absolute_error(y_train, y_pred_train):.4f}")
    
    print("\nTest Set:")
    print(f"  R² Score: {r2_score(y_test, y_pred_test):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_test)):.4f}")
    print(f"  MAE: {mean_absolute_error(y_test, y_pred_test):.4f}")
    
    # Feature importance
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE")
    print("="*60)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    for i, idx in enumerate(indices[:10]):
        print(f"{i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    
    return model

def main():
    """Main training pipeline"""
    print("="*60)
    print("FARMER CREDIT SCORE MODEL TRAINING")
    print("="*60)
    
    # Load data
    print("\nLoading training data...")
    df = load_training_data()
    print(f"✓ Loaded {len(df)} farmer records")
    
    # Prepare features
    print("\nPreparing features...")
    X, y, feature_names = prepare_features_and_labels(df)
    print(f"✓ Prepared {X.shape[1]} features")
    
    # Train model
    model = train_model(X, y, feature_names)
    
    # Save model
    model_path = 'model.joblib'
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to {model_path}")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
