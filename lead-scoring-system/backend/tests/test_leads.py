"""Tests for lead endpoints."""

import pytest
from fastapi import status


def test_create_lead(client, admin_headers):
    """Test creating a new lead."""
    response = client.post(
        "/api/leads",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "source": "website",
            "phone": "555-0123",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data
    assert "current_score" in data


def test_create_lead_duplicate_email(client, admin_headers):
    """Test creating lead with duplicate email fails."""
    # Create first lead
    client.post(
        "/api/leads",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "source": "website",
        },
        headers=admin_headers,
    )

    # Try to create duplicate
    response = client.post(
        "/api/leads",
        json={
            "name": "Jane Doe",
            "email": "john@example.com",
            "source": "website",
        },
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_list_leads(client, auth_headers):
    """Test listing leads."""
    response = client.get("/api/leads", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)


def test_get_lead_by_id(client, admin_headers):
    """Test getting a specific lead."""
    # Create a lead first
    create_response = client.post(
        "/api/leads",
        json={
            "name": "Test Lead",
            "email": "testlead@example.com",
            "source": "website",
        },
        headers=admin_headers,
    )
    lead_id = create_response.json()["id"]

    # Get the lead
    response = client.get(f"/api/leads/{lead_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == lead_id
    assert data["name"] == "Test Lead"


def test_get_nonexistent_lead(client, admin_headers):
    """Test getting a lead that doesn't exist."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/leads/{fake_id}", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

