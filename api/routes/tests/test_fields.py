from typing import Any
from tracker import app
from fastapi.testclient import TestClient

client = TestClient(app, base_url='http://127.0.0.1:8000')

def test_get_all_fields():
    response = client.get('/fields')
    assert response.status_code == 200
    assert type(response.json()) == list


def test_create_field_valid():
    response = client.post('/fields', json={
        "name": "F99",
        "acreage": 5.10,
        "yield_potential": 119,
        "crop": "wheat",
        "action": "harvest",
        "notes": "n/a",
        "farm_id": 1,
    })
    response_obj = response.json()
    assert response.status_code == 201
    assert response_obj['name'] == 'F99'


def test_create_field_duplicate():
    response = client.post('/fields', json={
        "name": "F99",
        "acreage": 5.10,
        "yield_potential": 119,
        "crop": "wheat",
        "action": "harvest",
        "notes": "n/a",
        "farm_id": 1,
    })
    response_obj = response.json()
    assert response.status_code == 500
    assert 'detail' in response_obj
    assert 'duplicate field record found' in response_obj['detail']


def test_get_field_by_id_valid_id():
    response = client.get('/fields/1')
    assert response.status_code == 200
    assert type(response.json()) == dict


def test_get_field_by_id_invalid_id():
    response = client.get('/fields/0')
    response_obj = response.json()
    assert response.status_code == 404
    assert response_obj['detail'] == 'field not found'


def test_modify_field_name_valid():
    response = client.put('/fields/1', json={
        "name": "F99",
        "acreage": "4.89",
        "yield_potential": "97",
        "crop": "corn",
        "action": "forage",
        "notes": "n/a",
        "farm_id": "1",
    })
    assert response.status_code == 204
