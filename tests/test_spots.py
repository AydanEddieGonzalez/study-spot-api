# Testing Spots database

SPOT = {
    "name": "Moffitt Library",
    "location": "Moffitt, 4th floor",
    "noise": "quiet",
    "has_outlets": True,
    "has_wifi": True,
    "hours": "8am to 2am",
}

def test_create_spot_returns_201_and_id(client):
    response = client.post("/spots", json=SPOT)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Moffitt Library"

def test_list_spots_starts_empty(client):
    response = client.get("/spots")

    assert response.status_code == 200
    assert response.json() == []

def test_get_spot_by_id(client):
    created = client.post("/spots", json=SPOT)
    spot_id = created.json()["id"]
    
    response = client.get(f"/spots/{spot_id}")

    assert response.status_code == 200
    assert response.json() == created.json()

def test_get_missing_spot_returns_404(client):
    response = client.get("/spots/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Spot not found"


def test_create_spot_with_bad_noise_returns_422(client):
    bad = {**SPOT, "noise": "silent"}
    response = client.post("/spots", json=bad)

    assert response.status_code == 422


def test_create_spot_with_empty_name_returns_422(client):
    bad = {**SPOT, "name": ""}

    response = client.post("/spots", json=bad)

    assert response.status_code == 422
