from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import User
from auth import get_password_hash

def test_register_user(client: TestClient, db: Session):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "agent"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify user in db
    user = db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.role == "agent"

def test_register_existing_username(client: TestClient, db: Session):
    # Create existing user
    user = User(
        username="existing",
        email="existing@example.com",
        hashed_password=get_password_hash("password123"),
        role="agent"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/register",
        json={
            "username": "existing",
            "email": "new@example.com",
            "password": "password123",
            "role": "agent"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_register_existing_email(client: TestClient, db: Session):
    # Create existing user
    user = User(
        username="user1",
        email="existing@example.com",
        hashed_password=get_password_hash("password123"),
        role="agent"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/register",
        json={
            "username": "user2",
            "email": "existing@example.com",
            "password": "password123",
            "role": "agent"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client: TestClient, db: Session):
    # Create user
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hashed,
        role="agent"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": password
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client: TestClient, db: Session):
    # Create user
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hashed,
        role="agent"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
