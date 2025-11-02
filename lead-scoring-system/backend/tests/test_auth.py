"""Tests for authentication endpoints."""

import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "securepassword123",
            "role": "sales_rep",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data  # Password should not be in response


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email fails."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "username": "differentuser",
            "full_name": "Different User",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails."""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "username" in data
    assert "role" in data


def test_get_current_user_unauthorized(client):
    """Test getting current user without token fails."""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

