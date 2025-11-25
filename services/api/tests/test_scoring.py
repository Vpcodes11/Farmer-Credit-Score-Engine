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

def test_compute_score_success(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create farmer with consent
    farmer = Farmer(
        farmer_id="FRM003",
        name="Score Test Farmer",
        mobile="7777777777",
        consent_given=True,
        land_area=2.5,
        crop_type="wheat",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    response = client.post(
        "/score",
        headers=headers,
        json={"farmer_id": "FRM003"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_id"] == "FRM003"
    assert "score" in data
    assert "drivers" in data
    assert len(data["drivers"]) > 0
    assert data["score"] >= 0 and data["score"] <= 100

def test_compute_score_no_consent(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    # Create farmer without consent
    farmer = Farmer(
        farmer_id="FRM004",
        name="No Consent Farmer",
        mobile="6666666666",
        consent_given=False,
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    response = client.post(
        "/score",
        headers=headers,
        json={"farmer_id": "FRM004"}
    )
    assert response.status_code == 403
    assert "consent required" in response.json()["detail"]

def test_compute_score_farmer_not_found(client: TestClient, db: Session):
    create_test_user(db)
    headers = get_auth_headers(client)
    
    response = client.post(
        "/score",
        headers=headers,
        json={"farmer_id": "NONEXISTENT"}
    )
    assert response.status_code == 404

def test_get_score_history(client: TestClient, db: Session):
    user = create_test_user(db)
    headers = get_auth_headers(client)
    
    farmer = Farmer(
        farmer_id="FRM005",
        name="History Farmer",
        mobile="5555555555",
        created_by=user.id
    )
    db.add(farmer)
    db.commit()
    
    # Add 2 scores
    s1 = Score(farmer_id=farmer.id, score=60, score_band="medium", computed_at=datetime.utcnow())
    s2 = Score(farmer_id=farmer.id, score=80, score_band="high", computed_at=datetime.utcnow())
    db.add_all([s1, s2])
    db.commit()
    
    response = client.get("/score/FRM005/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["scores"]) == 2
    # Should be ordered by date desc (though we used same time, order might vary in test)
    assert data["farmer_id"] == "FRM005"
