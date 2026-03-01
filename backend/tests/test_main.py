"""Tests for the CRUD API."""

import pytest
from fastapi.testclient import TestClient


def test_list_empty_items(client: TestClient) -> None:
    """Test listing items when database is empty."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_item(client: TestClient) -> None:
    """Test creating a new item."""
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    response = client.post("/", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1
    assert created["name"] == payload["name"]
    assert created["email"] == payload["email"]


def test_get_item(client: TestClient) -> None:
    """Test retrieving a specific item."""
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    client.post("/", json=payload)

    response = client.get("/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["name"] == payload["name"]
    assert item["email"] == payload["email"]


def test_get_nonexistent_item(client: TestClient) -> None:
    """Test retrieving an item that doesn't exist."""
    response = client.get("/999")
    assert response.status_code == 404


def test_update_item(client: TestClient) -> None:
    """Test updating an existing item."""
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    client.post("/", json=payload)

    update_payload = {"name": "Ada Byron", "email": "ada.b@example.com"}
    response = client.put("/1", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_payload["name"]
    assert updated["email"] == update_payload["email"]

    # Verify persistence
    response = client.get("/1")
    assert response.status_code == 200
    assert response.json()["name"] == update_payload["name"]


def test_update_nonexistent_item(client: TestClient) -> None:
    """Test updating an item that doesn't exist."""
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    response = client.put("/999", json=payload)
    assert response.status_code == 404


def test_delete_item(client: TestClient) -> None:
    """Test deleting an item."""
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    client.post("/", json=payload)

    response = client.delete("/1")
    assert response.status_code == 204

    # Verify deletion
    response = client.get("/1")
    assert response.status_code == 404


def test_delete_nonexistent_item(client: TestClient) -> None:
    """Test deleting an item that doesn't exist."""
    response = client.delete("/999")
    assert response.status_code == 404


def test_crud_flow(client: TestClient) -> None:
    """Test complete CRUD flow."""
    # Empty database
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []

    # Create
    payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
    response = client.post("/", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1
    assert created["name"] == payload["name"]
    assert created["email"] == payload["email"]

    # Read all
    response = client.get("/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Read inserted item
    response = client.get("/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["name"] == payload["name"]
    assert item["email"] == payload["email"]

    # Update
    update_payload = {"name": "Ada Byron", "email": "ada.b@example.com"}
    response = client.put("/1", json=update_payload)
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["name"] == update_payload["name"]
    assert item["email"] == update_payload["email"]

    # Re-read inserted
    response = client.get("/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["name"] == update_payload["name"]
    assert item["email"] == update_payload["email"]

    # Delete
    response = client.delete("/1")
    assert response.status_code == 204

    # Verify deleted
    response = client.get("/1")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "invalid_email",
    [
        "not-an-email",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com",
    ],
)
def test_create_invalid_email(client: TestClient, invalid_email: str) -> None:
    """Test creating item with invalid email."""
    payload = {"name": "Ada Lovelace", "email": invalid_email}
    response = client.post("/", json=payload)
    assert response.status_code == 422


def test_create_empty_name(client: TestClient) -> None:
    """Test creating item with empty name."""
    payload = {"name": "", "email": "ada@example.com"}
    response = client.post("/", json=payload)
    assert response.status_code == 422
