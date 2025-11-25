from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import User, Farmer, Score
from auth import get_password_hash
from datetime import datetime

def create_test_user(db: Session, role: str = "agent") -> User:
    user = User(
        username=f"test{role}",
        email=f"test{role}@example.com",
        hashed_password=get_password_hash("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_headers(client: TestClient, username: str = "testagent"):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_loan_quote_eligible(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create farmer with high score
    farmer = Farmer(
        farmer_id="FRM006",
        name="Eligible Farmer",
        mobile="4444444444",
        land_area=2.0,
        crop_type="wheat",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    score = Score(
        farmer_id=farmer.id,
        score=75.0,
        score_band="high",
        computed_at=datetime.utcnow()
    )
    db.add(score)
    db.commit()
    
    response = client.post(
        "/loan/quote",
        headers=headers,
        json={"farmer_id": "FRM006"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is True
    assert data["credit_score"] == 75.0
    assert len(data["emi_plans"]) > 0
    assert data["crop_cycle_months"] == 5  # Wheat

def test_get_loan_quote_ineligible(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create farmer with low score
    farmer = Farmer(
        farmer_id="FRM007",
        name="Ineligible Farmer",
        mobile="3333333333",
        land_area=2.0,
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    score = Score(
        farmer_id=farmer.id,
        score=20.0,
        score_band="low",
        computed_at=datetime.utcnow()
    )
    db.add(score)
    db.commit()
    
    response = client.post(
        "/loan/quote",
        headers=headers,
        json={"farmer_id": "FRM007"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert "not recommended" in data["remarks"].lower()

def test_get_loan_quote_no_score(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    farmer = Farmer(
        farmer_id="FRM008",
        name="No Score Farmer",
        mobile="2222222222",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    response = client.post(
        "/loan/quote",
        headers=headers,
        json={"farmer_id": "FRM008"}
    )
    assert response.status_code == 400
    assert "compute score first" in response.json()["detail"].lower()
