import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.services import get_password_hash

def test_create_user(client, db_session: Session):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data

def test_create_user_duplicate_email(client, db_session: Session):
    # Cria um usuário existente
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenta criar outro usuário com o mesmo email
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Another User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client, db_session: Session):
    # Cria um usuário
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenta fazer login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db_session: Session):
    # Cria um usuário
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenta fazer login com senha errada
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, db_session: Session):
    # Cria um usuário
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Faz login para obter o token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Tenta obter os dados do usuário atual
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email
    assert data["full_name"] == user.full_name

def test_get_current_user_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_no_token(client):
    """Testa a obtenção do usuário atual sem token"""
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]

def test_change_password_success(client, auth_headers):
    """Testa a alteração de senha bem-sucedida"""
    response = client.put(
        "/auth/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password updated successfully"

def test_change_password_wrong_current_password(client, auth_headers):
    """Testa a alteração de senha com senha atual incorreta"""
    response = client.put(
        "/auth/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Current password is incorrect" in response.json()["detail"]

def test_change_password_weak_new_password(client, auth_headers):
    """Testa a alteração de senha com nova senha fraca"""
    response = client.put(
        "/auth/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "123"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Password does not meet requirements" in response.json()["detail"] 