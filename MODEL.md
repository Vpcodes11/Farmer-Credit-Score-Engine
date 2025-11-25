# Farmer Credit Score Model Documentation

## Overview

The Farmer Credit Score (FCS) model computes a transparent credit score from 0-100 for farmers using a combination of traditional credit data, satellite imagery, weather patterns, and alternative data sources.

## Scoring Formula

### Deterministic Scoring (Fallback)

The deterministic model uses a weighted sum of normalized features:

```
FCS = Σ (normalized_feature_i × weight_i) × 100
```

Where each feature is normalized to [0, 1] range and multiplied by its weight.

### Feature Weights

| Feature | Weight | Range | Normalization |
|---------|--------|-------|---------------|
| `land_area` | 8% | 0.5-10 ha | Linear |
| `crop_type` | 6% | Categorical | Encoded (rice=0.8, wheat=0.9, cotton=0.7, maize=0.75) |
| `last_year_yield_est` | 12% | 1.5-5.0 tons/ha | Linear |
| `ndvi_mean` | 15% | 0.2-0.9 | Linear |
| `ndvi_trend` | 10% | -0.15 to +0.15 | Linear |
| `rainfall_anomaly_3mo` | 8% | -50 to +50 mm | Inverse absolute deviation from 0 |
| `past_kcc_defaults` | 15% | 0-3+ | Inverse linear |
| `upi_txn_freq` | 10% | 0-50/month | Linear |
| `market_price_volatility` | 6% | 5-30% | Inverse linear |
| `fpo_membership_flag` | 5% | 0 or 1 | Binary |
| `distance_to_mandi_km` | 5% | 2-50 km | Inverse linear |

### RandomForest Model

**Architecture:**
- Algorithm: RandomForestRegressor (scikit-learn)
- Trees: 100
- Max depth: 10
- Min samples split: 5
- Min samples leaf: 2

**Training Data:**
- 200 synthetic farmer profiles
- 80/20 train/test split
- Features: 11 normalized inputs
- Labels: Deterministic scores (normalized to 0-1)

**Performance (on synthetic data):**
- R² Score: ~0.95
- RMSE: ~0.03
- MAE: ~0.02

## Explainability (SHAP)

### SHAP TreeExplainer

We use SHAP (SHapley Additive exPlanations) to provide transparent explanations for each score.

**Process:**
1. Compute SHAP values for each feature
2. Rank features by absolute SHAP value
3. Select top 3 features
4. Generate human-readable explanations

**Example SHAP Output:**

```python
{
  "feature": "ndvi_mean",
  "shap_value": -0.12,  # Impact on score (scaled to 0-100)
  "explanation": "Lower crop vigor detected from satellite"
}
```

### Driver Explanations

Each driver includes:
- **Feature name**: Human-readable (e.g., "Crop health (satellite)")
- **Impact**: Positive or negative contribution to score
- **Explanation**: Context-specific text explaining the impact

**Explanation Templates:**

| Feature | Positive | Negative |
|---------|----------|----------|
| `ndvi_mean` | "Strong crop health observed from satellite" | "Lower crop vigor detected from satellite" |
| `past_kcc_defaults` | "Clean credit history" | "X default(s) in KCC history" |
| `rainfall_anomaly_3mo` | "Favorable rainfall pattern" | "Excess/Delayed rainfall observed" |
| `upi_txn_freq` | "Active digital transaction history" | "Limited digital payment activity" |

## Training Process

### Data Generation

```bash
# Generate synthetic data
python scripts/generate_synthetic_data.py

# Output:
# - sample_data/farmers.csv (200 farmers)
# - sample_data/satellite.csv (NDVI time series)
# - sample_data/weather.csv (Weather observations)
```

**Data Distribution:**
- 50 rice farmers
- 50 wheat farmers
- 50 cotton farmers
- 50 maize farmers
- Score distribution: 20% low (0-40), 50% medium (41-70), 30% high (71-100)

### Model Training

```bash
# Train RandomForest model
cd services/ml
python train.py

# Output:
# - model.joblib (trained model)
# - Training metrics printed to console
```

**Training Output:**
```
Training set: 160 samples
Test set: 40 samples

MODEL PERFORMANCE
==================
Training Set:
  R² Score: 0.9876
  RMSE: 0.0234
  MAE: 0.0189

Test Set:
  R² Score: 0.9543
  RMSE: 0.0312
  MAE: 0.0245

FEATURE IMPORTANCE
==================
1. ndvi_mean: 0.1823
2. past_kcc_defaults: 0.1654
3. last_year_yield_est: 0.1432
...
```

## Feature Engineering

### NDVI (Normalized Difference Vegetation Index)

**Source**: Satellite imagery (Sentinel-2 or similar)

**Calculation**:
```
NDVI = (NIR - Red) / (NIR + Red)
```

**Interpretation**:
- 0.2-0.3: Bare soil / sparse vegetation
- 0.3-0.6: Moderate vegetation
- 0.6-0.9: Dense, healthy vegetation

**Features Derived**:
- `ndvi_mean`: Average NDVI over last 3 months
- `ndvi_trend`: Linear trend (positive = improving, negative = declining)

### Rainfall Anomaly

**Calculation**:
```
anomaly = actual_rainfall_3mo - historical_avg_3mo
```

**Interpretation**:
- Negative: Drought conditions
- Near zero: Normal rainfall
- Positive: Excess rainfall

**Impact on Score**:
- Optimal: Near zero (normal rainfall)
- Penalized: Large deviations (drought or flood)

### Alternative Data

**UPI Transaction Frequency**:
- Proxy for financial activity and digital literacy
- Higher frequency → better score

**FPO Membership**:
- Binary flag (member = 1, non-member = 0)
- Members get slight score boost (access to better inputs, markets)

**Distance to Mandi**:
- Proxy for market access
- Closer to market → better score

## Score Bands

| Band | Range | Interpretation | Loan Eligibility |
|------|-------|----------------|------------------|
| Low | 0-40 | High risk | Not recommended |
| Medium | 41-70 | Moderate risk | Standard rates |
| High | 71-100 | Low risk | Premium rates |

## Model Versioning

**Current Version**: 1.0

**Version History**:
- v1.0 (2024-11-25): Initial release with RandomForest + SHAP

**Future Improvements**:
- v1.1: Add soil health data
- v1.2: Incorporate market linkage data
- v2.0: Deep learning model with time-series forecasting

## Validation & Testing

### Unit Tests

```bash
# Test feature extraction
pytest services/ml/tests/test_features.py

# Test scoring logic
pytest services/ml/tests/test_scoring.py
```

### Integration Tests

```bash
# Test end-to-end scoring
pytest services/api/tests/test_scoring.py
```

### Fairness & Bias

**Considerations**:
- Model trained on synthetic data (no real farmer bias)
- Features are objective (satellite, weather, transactions)
- Explainability ensures transparency

**Monitoring**:
- Track score distribution by crop type, region
- Monitor for systematic biases
- Regular model retraining with updated data

## Deployment

### Model Artifacts

```
services/ml/
├── model.joblib          # Trained RandomForest model
├── features.py           # Feature engineering
├── scoring.py            # Deterministic scoring
├── model.py              # ML model wrapper
└── train.py              # Training script
```

### API Integration

```python
from model import get_model

# Load model
model = get_model('model.joblib')

# Predict
farmer_data = {...}
score, drivers = model.predict(farmer_data)

# Output:
# score: 74.5
# drivers: [
#   {"feature": "...", "impact": -12, "explanation": "..."},
#   ...
# ]
```

### Fallback Behavior

If ML model fails to load or predict:
1. Automatically fall back to deterministic scoring
2. Log warning
3. Return score with `model_type: "deterministic"`

## References

- **SHAP**: Lundberg & Lee (2017). "A Unified Approach to Interpreting Model Predictions"
- **NDVI**: Rouse et al. (1974). "Monitoring Vegetation Systems"
- **RandomForest**: Breiman (2001). "Random Forests"

---

**Last Updated**: 2024-11-25  
**Model Version**: 1.0  
**Contact**: ml-team@example.com
