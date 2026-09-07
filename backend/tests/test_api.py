import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_serve_index(client):
    """Test serving index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_upload_demo_bill(client):
    """Test uploading demo bill."""
    response = client.post("/api/upload?demo=true")
    assert response.status_code == 200
    
    data = response.json()
    assert "restaurant_name" in data
    assert "items" in data
    assert data["restaurant_name"] == "Spice Garden"


def test_upload_without_file(client):
    """Test upload without file should return error."""
    response = client.post("/api/upload")
    assert response.status_code == 200
    assert "error" in response.json()


def test_calculate_endpoint(client):
    """Test calculate endpoint with valid data."""
    payload = {
        "bill": {
            "restaurant_name": "Test Restaurant",
            "date": "2024-01-15",
            "bill_number": "INV-001",
            "items": [
                {
                    "id": "item-1",
                    "name": "Biryani",
                    "quantity": 2,
                    "unit_price": "300",
                    "total": "600",
                    "confidence": 0.95
                }
            ],
            "subtotal": "600",
            "tax": "54",
            "service_charge": "60",
            "discount": "0",
            "printed_total": "714"
        },
        "members": [
            {"id": "member-1", "name": "Rahul"},
            {"id": "member-2", "name": "Priya"}
        ],
        "assignments": [
            {
                "item_id": "item-1",
                "member_ids": ["member-1", "member-2"]
            }
        ]
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "members" in data
    assert "bill_total" in data
    assert "verification" in data
    assert len(data["members"]) == 2


def test_calculate_with_too_few_members(client):
    """Test calculate with too few members."""
    payload = {
        "bill": {
            "restaurant_name": "Test Restaurant",
            "date": "2024-01-15",
            "items": [
                {
                    "id": "item-1",
                    "name": "Biryani",
                    "quantity": 2,
                    "unit_price": "300",
                    "total": "600",
                    "confidence": 0.95
                }
            ],
            "subtotal": "600",
            "tax": "54",
            "service_charge": "60",
            "discount": "0",
            "printed_total": "714"
        },
        "members": [
            {"id": "member-1", "name": "Rahul"}
        ],
        "assignments": [
            {
                "item_id": "item-1",
                "member_ids": ["member-1"]
            }
        ]
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400


def test_calculate_with_no_assignments(client):
    """Test calculate with no assignments."""
    payload = {
        "bill": {
            "restaurant_name": "Test Restaurant",
            "date": "2024-01-15",
            "items": [
                {
                    "id": "item-1",
                    "name": "Biryani",
                    "quantity": 2,
                    "unit_price": "300",
                    "total": "600",
                    "confidence": 0.95
                }
            ],
            "subtotal": "600",
            "tax": "54",
            "service_charge": "60",
            "discount": "0",
            "printed_total": "714"
        },
        "members": [
            {"id": "member-1", "name": "Rahul"},
            {"id": "member-2", "name": "Priya"}
        ],
        "assignments": []
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400


def test_calculate_with_invalid_item_price(client):
    """Test calculate with invalid item price."""
    payload = {
        "bill": {
            "restaurant_name": "Test Restaurant",
            "date": "2024-01-15",
            "items": [
                {
                    "id": "item-1",
                    "name": "Biryani",
                    "quantity": 2,
                    "unit_price": "-300",
                    "total": "-600",
                    "confidence": 0.95
                }
            ],
            "subtotal": "-600",
            "tax": "0",
            "service_charge": "0",
            "discount": "0",
            "printed_total": "-600"
        },
        "members": [
            {"id": "member-1", "name": "Rahul"}
        ],
        "assignments": [
            {
                "item_id": "item-1",
                "member_ids": ["member-1"]
            }
        ]
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
