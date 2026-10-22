from fastapi.testclient import TestClient
from studyspots.main import app

client = TestClient(app)

def test_():
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}