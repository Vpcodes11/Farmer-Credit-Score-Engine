"""
Synthetic Data Generator for Farmer Credit Score Engine
Generates realistic farmer profiles, satellite data, and weather data for testing.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
SEED = 42
np.random.seed(SEED)

# Constants
NUM_FARMERS = 200
CROP_TYPES = ['rice', 'wheat', 'cotton', 'maize']
STATES = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka']

def generate_farmers():
    """Generate synthetic farmer profiles"""
    farmers = []
    
    for i in range(NUM_FARMERS):
        farmer_id = f"FRM{str(i+1).zfill(6)}"
        crop_type = np.random.choice(CROP_TYPES)
        state = np.random.choice(STATES)
        
        # Generate realistic features
        land_area = np.random.uniform(0.5, 10.0)  # hectares
        last_year_yield = np.random.uniform(1.5, 5.0) * land_area  # tons
        
        # NDVI values (0.2 to 0.9, higher is better)
        ndvi_mean = np.random.uniform(0.3, 0.85)
        ndvi_trend = np.random.uniform(-0.15, 0.15)
        
        # Rainfall anomaly (-50 to +50 mm)
        rainfall_anomaly_3mo = np.random.uniform(-50, 50)
        
        # Credit history
        past_kcc_defaults = np.random.choice([0, 0, 0, 1, 2], p=[0.6, 0.25, 0.1, 0.04, 0.01])
        
        # Alternative data
        upi_txn_freq = np.random.randint(0, 50)  # transactions per month
        market_price_volatility = np.random.uniform(5, 30)  # percentage
        fpo_membership = np.random.choice([0, 1], p=[0.6, 0.4])
        distance_to_mandi = np.random.uniform(2, 50)  # km
        
        # Generate geo coordinates (approximate Indian agricultural regions)
        lat = np.random.uniform(15.0, 30.0)
        lon = np.random.uniform(72.0, 85.0)
        
        farmer = {
            'farmer_id': farmer_id,
            'name': f"Farmer {i+1}",
            'mobile': f"+91{''.join([str(np.random.randint(0, 10)) for _ in range(10)])}",
            'aadhar': f"{np.random.randint(1000, 9999)} {np.random.randint(1000, 9999)} {np.random.randint(1000, 9999)}",
            'state': state,
            'district': f"District {np.random.randint(1, 20)}",
            'village': f"Village {np.random.randint(1, 100)}",
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'land_area': round(land_area, 2),
            'crop_type': crop_type,
            'last_year_yield_est': round(last_year_yield, 2),
            'ndvi_mean': round(ndvi_mean, 3),
            'ndvi_trend': round(ndvi_trend, 3),
            'rainfall_anomaly_3mo': round(rainfall_anomaly_3mo, 1),
            'past_kcc_defaults': past_kcc_defaults,
            'upi_txn_freq': upi_txn_freq,
            'market_price_volatility': round(market_price_volatility, 1),
            'fpo_membership_flag': fpo_membership,
            'distance_to_mandi_km': round(distance_to_mandi, 1),
            'consent_given': True,
            'created_at': (datetime.now() - timedelta(days=np.random.randint(1, 365))).isoformat()
        }
        
        farmers.append(farmer)
    
    return pd.DataFrame(farmers)

def generate_satellite_data(farmers_df):
    """Generate synthetic satellite NDVI time series"""
    satellite_data = []
    
    for _, farmer in farmers_df.iterrows():
        land_id = f"LAND{farmer['farmer_id'][3:]}"
        base_ndvi = farmer['ndvi_mean']
        trend = farmer['ndvi_trend']
        
        # Generate 12 months of NDVI data
        for month in range(12):
            date = datetime.now() - timedelta(days=30 * (12 - month))
            # Add seasonal variation and trend
            seasonal_factor = 0.1 * np.sin(2 * np.pi * month / 12)
            noise = np.random.normal(0, 0.05)
            ndvi = base_ndvi + trend * (month / 12) + seasonal_factor + noise
            ndvi = max(0.1, min(0.9, ndvi))  # Clamp to valid range
            
            satellite_data.append({
                'land_id': land_id,
                'farmer_id': farmer['farmer_id'],
                'date': date.strftime('%Y-%m-%d'),
                'ndvi': round(ndvi, 3),
                'cloud_cover': round(np.random.uniform(0, 40), 1)
            })
    
    return pd.DataFrame(satellite_data)

def generate_weather_data(farmers_df):
    """Generate synthetic weather data"""
    weather_data = []
    
    # Group by approximate location
    locations = farmers_df[['latitude', 'longitude', 'state']].drop_duplicates()
    
    for _, loc in locations.iterrows():
        geo_key = f"{round(loc['latitude'], 1)}_{round(loc['longitude'], 1)}"
        
        # Generate 90 days of weather data
        for day in range(90):
            date = datetime.now() - timedelta(days=90 - day)
            
            # Seasonal rainfall pattern
            month = date.month
            if month in [6, 7, 8, 9]:  # Monsoon
                rainfall = np.random.exponential(8)
            elif month in [10, 11]:  # Post-monsoon
                rainfall = np.random.exponential(3)
            else:  # Dry season
                rainfall = np.random.exponential(0.5)
            
            weather_data.append({
                'geo_key': geo_key,
                'latitude': loc['latitude'],
                'longitude': loc['longitude'],
                'state': loc['state'],
                'date': date.strftime('%Y-%m-%d'),
                'rainfall_mm': round(rainfall, 1),
                'temperature_max': round(np.random.uniform(28, 42), 1),
                'temperature_min': round(np.random.uniform(15, 28), 1),
                'humidity': round(np.random.uniform(40, 90), 1)
            })
    
    return pd.DataFrame(weather_data)

def main():
    """Generate all synthetic datasets"""
    print("Generating synthetic data...")
    print(f"Random seed: {SEED}")
    
    # Generate farmers
    print(f"\nGenerating {NUM_FARMERS} farmer profiles...")
    farmers_df = generate_farmers()
    farmers_df.to_csv('sample_data/farmers.csv', index=False)
    print(f"✓ Created farmers.csv ({len(farmers_df)} records)")
    
    # Generate satellite data
    print("\nGenerating satellite NDVI data...")
    satellite_df = generate_satellite_data(farmers_df)
    satellite_df.to_csv('sample_data/satellite.csv', index=False)
    print(f"✓ Created satellite.csv ({len(satellite_df)} records)")
    
    # Generate weather data
    print("\nGenerating weather data...")
    weather_df = generate_weather_data(farmers_df)
    weather_df.to_csv('sample_data/weather.csv', index=False)
    print(f"✓ Created weather.csv ({len(weather_df)} records)")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"\nFarmers by crop type:")
    print(farmers_df['crop_type'].value_counts())
    print(f"\nFarmers by state:")
    print(farmers_df['state'].value_counts())
    print(f"\nLand area statistics (hectares):")
    print(farmers_df['land_area'].describe())
    print(f"\nNDVI mean statistics:")
    print(farmers_df['ndvi_mean'].describe())
    print(f"\nPast KCC defaults distribution:")
    print(farmers_df['past_kcc_defaults'].value_counts())
    
    print("\n✓ All synthetic data generated successfully!")

if __name__ == '__main__':
    main()
