import pytest

SPOTS = [
    ({"name": "Moffitt Library", "location": "Moffitt", "noise": "quiet",
      "has_outlets": True, "has_wifi": True}, [5, 5]),
    ({"name": "Gardner Main Stacks", "location": "Below Doe", "noise": "quiet",
      "has_outlets": False, "has_wifi": True}, [3]),
    ({"name": "MLK Student Union", "location": "Lower Sproul", "noise": "loud",
      "has_outlets": True, "has_wifi": True}, [2, 3]),
    ({"name": "Caffe Strada", "location": "College Ave", "noise": "moderate",
      "has_outlets": False, "has_wifi": False}, []),
]


@pytest.fixture
def seeded_client(client):
    for spot, scores in SPOTS:
        spot_id = client.post("/spots", json=spot).json()["id"]
        for score in scores:
            client.post(f"/spots/{spot_id}/ratings", json={"score": score})
    return client


def names(response):
    return [s["name"] for s in response.json()]


@pytest.mark.parametrize(
    "params, expected",
    [
        ({}, {"Moffitt Library", "Gardner Main Stacks", "MLK Student Union", "Caffe Strada"}),
        ({"noise": "quiet"}, {"Moffitt Library", "Gardner Main Stacks"}),
        ({"outlets": "false"}, {"Gardner Main Stacks", "Caffe Strada"}),
        ({"wifi": "false"}, {"Caffe Strada"}),
        ({"q": "MOFF"}, {"Moffitt Library"}),
        ({"min_rating": 4}, {"Moffitt Library"}),
        ({"min_rating": 2.5}, {"Moffitt Library", "Gardner Main Stacks", "MLK Student Union"}),
        ({"noise": "quiet", "outlets": "true", "min_rating": 4}, {"Moffitt Library"}),
    ],
)
def test_filters(seeded_client, params, expected):
    response = seeded_client.get("/spots", params=params)

    assert response.status_code == 200
    assert set(names(response)) == expected


def test_sort_by_rating(seeded_client):
    response = seeded_client.get("/spots", params={"sort": "rating"})

    assert response.status_code == 200
    assert names(response) == [
        "Moffitt Library",
        "Gardner Main Stacks",
        "MLK Student Union",
        "Caffe Strada",  
    ]


def test_sort_by_name(seeded_client):
    response = seeded_client.get("/spots", params={"sort": "name"})
    
    assert response.status_code == 200
    assert names(response) == [
        "Caffe Strada",
        "Gardner Main Stacks",
        "MLK Student Union",
        "Moffitt Library",
    ]


@pytest.mark.parametrize("params", [{"min_rating": 9}, {"sort": "price"}, {"noise": "silent"}])
def test_bad_params_return_422(seeded_client, params):
    response = seeded_client.get("/spots", params=params)

    assert response.status_code == 422