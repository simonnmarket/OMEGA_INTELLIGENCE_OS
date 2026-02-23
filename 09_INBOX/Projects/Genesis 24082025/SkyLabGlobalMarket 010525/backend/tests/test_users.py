import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User
from app.services import get_password_hash

def get_auth_token(client, email: str, password: str):
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_user(db_session: Session):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_create_user(client):
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "full_name": "New User"
    }
    
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data

def test_create_user_duplicate_email(client, test_user):
    user_data = {
        "email": test_user.email,
        "password": "newpassword",
        "full_name": "Another User"
    }
    
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_current_user(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name

def test_update_user(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    update_data = {
        "full_name": "Updated User",
        "email": "updated@example.com"
    }
    
    response = client.put(
        "/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

def test_change_password(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    password_data = {
        "current_password": "testpassword",
        "new_password": "newpassword"
    }
    
    response = client.put(
        "/users/me/password",
        json=password_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica se a nova senha funciona
    new_token = get_auth_token(client, test_user.email, "newpassword")
    assert new_token is not None

def test_change_password_wrong_current(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword"
    }
    
    response = client.put(
        "/users/me/password",
        json=password_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_user(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica se o usuário foi realmente deletado
    response = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 