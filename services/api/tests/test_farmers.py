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

def test_onboard_farmer(client: TestClient, db: Session):
    create_test_user(db)
    headers = get_auth_headers(client)
    
    response = client.post(
        "/farmers",
        headers=headers,
        json={
            "farmer_id": "FRM001",
            "name": "Ramesh Kumar",
            "mobile": "9876543210",
            "state": "Punjab",
            "district": "Ludhiana",
            "village": "Manwal",
            "land_area": 2.5,
            "crop_type": "wheat",
            "consent_given": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["farmer_id"] == "FRM001"
    assert data["name"] == "Ramesh Kumar"
    
    # Verify in db
    farmer = db.query(Farmer).filter(Farmer.farmer_id == "FRM001").first()
    assert farmer is not None
    assert farmer.consent_given is True

def test_onboard_existing_farmer(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create existing farmer
    farmer = Farmer(
        farmer_id="FRM001",
        name="Existing Farmer",
        mobile="9999999999",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    response = client.post(
        "/farmers",
        headers=headers,
        json={
            "farmer_id": "FRM001",
            "name": "New Name",
            "mobile": "9876543210"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_farmer(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create farmer with score
    farmer = Farmer(
        farmer_id="FRM002",
        name="Suresh Singh",
        mobile="8888888888",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    score = Score(
        farmer_id=farmer.id,
        score=75.5,
        score_band="high",
        computed_at=datetime.utcnow()
    )
    db.add(score)
    db.commit()
    
    response = client.get(f"/farmers/FRM002", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_id"] == "FRM002"
    assert data["latest_score"] == 75.5

def test_list_farmers(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create 2 farmers
    f1 = Farmer(farmer_id="F1", name="Farmer 1", mobile="111", created_by=user.id)
    f2 = Farmer(farmer_id="F2", name="Farmer 2", mobile="222", created_by=user.id)
    db.add_all([f1, f2])
    db.commit()
    
    response = client.get("/farmers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["farmer_id"] == "F1"
    assert data[1]["farmer_id"] == "F2"
