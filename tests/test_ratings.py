SPOT = {
    "name": "Moffitt Library",
    "location": "Moffitt, 4th floor",
    "noise": "quiet",
    "has_outlets": True,
    "has_wifi": True,
}


def make_spot(client):
    return client.post("/spots", json=SPOT).json()["id"]


def test_patch_changes_only_sent_field(client):
    spot_id = make_spot(client)

    response = client.patch(f"/spots/{spot_id}", json={"noise": "loud"})

    assert response.status_code == 200
    data = response.json()
    assert data["noise"] == "loud"
    assert data["name"] == "Moffitt Library"
    assert data["location"] == "Moffitt, 4th floor"


def test_delete_then_get_returns_404(client):
    spot_id = make_spot(client)

    response = client.delete(f"/spots/{spot_id}")
    assert response.status_code == 204

    response = client.get(f"/spots/{spot_id}")
    assert response.status_code == 404


def test_rating_missing_spot_returns_404(client):
    response = client.post("/spots/999/ratings", json={"score": 5})

    assert response.status_code == 404
    assert response.json()["detail"] == "Spot not found"


def test_average_rating(client):
    spot_id = make_spot(client)
    for score in [5, 4, 3]:
        client.post(f"/spots/{spot_id}/ratings", json={"score": score})

    response = client.get(f"/spots/{spot_id}")

    data = response.json()
    assert data["avg_rating"] == 4.0
    assert data["rating_count"] == 3


def test_unrated_spot_has_null_average(client):
    spot_id = make_spot(client)

    response = client.get(f"/spots/{spot_id}")

    data = response.json()
    assert data["avg_rating"] is None
    assert data["rating_count"] == 0
