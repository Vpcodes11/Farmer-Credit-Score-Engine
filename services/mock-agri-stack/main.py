"""
Mock Agri Stack API Service
Simulates government Agri Stack endpoints for development/testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import os
import random

app = FastAPI(
    title="Mock Agri Stack API",
    version="1.0.0",
    description="Simulated Agri Stack endpoints for testing"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
DATA_DIR = os.getenv("DATA_DIR", "/app/data")

try:
    farmers_df = pd.read_csv(os.path.join(DATA_DIR, "farmers.csv"))
    satellite_df = pd.read_csv(os.path.join(DATA_DIR, "satellite.csv"))
    weather_df = pd.read_csv(os.path.join(DATA_DIR, "weather.csv"))
    print(f"✓ Loaded {len(farmers_df)} farmers, {len(satellite_df)} satellite records, {len(weather_df)} weather records")
except Exception as e:
    print(f"Warning: Could not load data files: {e}")
    farmers_df = pd.DataFrame()
    satellite_df = pd.DataFrame()
    weather_df = pd.DataFrame()

# Response models
class LandParcel(BaseModel):
    land_id: str
    area: float
    crop_type: str
    sowing_date: Optional[str]
    survey_number: str

class FarmerData(BaseModel):
    farmer_id: str
    name: str
    mobile: str
    aadhar: Optional[str]
    state: str
    district: str
    village: str
    land_parcels: List[LandParcel]

class LandDetails(BaseModel):
    land_id: str
    area: float
    crop_type: str
    soil_type: str
    irrigation_type: str
    ownership_type: str

class NDVIReading(BaseModel):
    date: str
    ndvi: float
    cloud_cover: float

class SatelliteData(BaseModel):
    land_id: str
    readings: List[NDVIReading]

class WeatherData(BaseModel):
    geo_key: str
    latitude: float
    longitude: float
    recent_rainfall_mm: float
    avg_temperature: float
    humidity: float
    forecast: str

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Mock Agri Stack API",
        "version": "1.0.0",
        "endpoints": [
            "/mock/farmer/{farmer_id}",
            "/mock/land/{land_id}",
            "/mock/satellite/{land_id}",
            "/mock/weather/{geo}"
        ]
    }

@app.get("/mock/farmer/{farmer_id}", response_model=FarmerData)
def get_farmer(farmer_id: str):
    """
    Get farmer data from mock Agri Stack
    
    Args:
        farmer_id: Farmer ID
    
    Returns:
        Farmer data with land parcels
    """
    if farmers_df.empty:
        raise HTTPException(status_code=503, detail="Data not available")
    
    farmer = farmers_df[farmers_df['farmer_id'] == farmer_id]
    
    if farmer.empty:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    
    farmer_row = farmer.iloc[0]
    
    # Generate land parcel
    land_id = f"LAND{farmer_id[3:]}"
    land_parcel = LandParcel(
        land_id=land_id,
        area=farmer_row['land_area'],
        crop_type=farmer_row['crop_type'],
        sowing_date=(datetime.now() - timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d'),
        survey_number=f"SY{random.randint(100, 999)}/{random.randint(1, 50)}"
    )
    
    return FarmerData(
        farmer_id=farmer_row['farmer_id'],
        name=farmer_row['name'],
        mobile=farmer_row['mobile'],
        aadhar=farmer_row.get('aadhar'),
        state=farmer_row['state'],
        district=farmer_row['district'],
        village=farmer_row['village'],
        land_parcels=[land_parcel]
    )

@app.get("/mock/land/{land_id}", response_model=LandDetails)
def get_land(land_id: str):
    """
    Get land record details
    
    Args:
        land_id: Land ID
    
    Returns:
        Land details
    """
    if farmers_df.empty:
        raise HTTPException(status_code=503, detail="Data not available")
    
    # Extract farmer ID from land ID
    farmer_id = f"FRM{land_id[4:]}"
    farmer = farmers_df[farmers_df['farmer_id'] == farmer_id]
    
    if farmer.empty:
        raise HTTPException(status_code=404, detail=f"Land {land_id} not found")
    
    farmer_row = farmer.iloc[0]
    
    return LandDetails(
        land_id=land_id,
        area=farmer_row['land_area'],
        crop_type=farmer_row['crop_type'],
        soil_type=random.choice(['Loamy', 'Clay', 'Sandy', 'Black']),
        irrigation_type=random.choice(['Rainfed', 'Canal', 'Borewell', 'Drip']),
        ownership_type='Owned'
    )

@app.get("/mock/satellite/{land_id}", response_model=SatelliteData)
def get_satellite(land_id: str):
    """
    Get satellite NDVI data for land parcel
    
    Args:
        land_id: Land ID
    
    Returns:
        NDVI time series
    """
    if satellite_df.empty:
        raise HTTPException(status_code=503, detail="Data not available")
    
    # Get satellite data for this land
    sat_data = satellite_df[satellite_df['land_id'] == land_id]
    
    if sat_data.empty:
        raise HTTPException(status_code=404, detail=f"No satellite data for {land_id}")
    
    readings = []
    for _, row in sat_data.iterrows():
        readings.append(NDVIReading(
            date=row['date'],
            ndvi=row['ndvi'],
            cloud_cover=row['cloud_cover']
        ))
    
    return SatelliteData(
        land_id=land_id,
        readings=readings
    )

@app.get("/mock/weather/{geo}", response_model=WeatherData)
def get_weather(geo: str):
    """
    Get weather data for location
    
    Args:
        geo: Geo key (lat_lon format)
    
    Returns:
        Weather data
    """
    if weather_df.empty:
        raise HTTPException(status_code=503, detail="Data not available")
    
    # Try to find matching geo key
    weather = weather_df[weather_df['geo_key'] == geo]
    
    if weather.empty:
        # Return default data
        return WeatherData(
            geo_key=geo,
            latitude=25.0,
            longitude=75.0,
            recent_rainfall_mm=50.0,
            avg_temperature=30.0,
            humidity=65.0,
            forecast="Partly cloudy"
        )
    
    # Get recent data
    recent = weather.tail(7)
    
    return WeatherData(
        geo_key=geo,
        latitude=recent.iloc[0]['latitude'],
        longitude=recent.iloc[0]['longitude'],
        recent_rainfall_mm=round(recent['rainfall_mm'].sum(), 1),
        avg_temperature=round(recent['temperature_max'].mean(), 1),
        humidity=round(recent['humidity'].mean(), 1),
        forecast=random.choice(['Clear sky', 'Partly cloudy', 'Cloudy', 'Light rain expected'])
    )

@app.get("/healthz")
def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
