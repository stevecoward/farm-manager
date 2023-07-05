from typing import Any
from tracker import app
from fastapi.testclient import TestClient

client = TestClient(app, base_url='http://127.0.0.1:8000')

def test_get_all_workers():
    response = client.get('/workers')
    assert response.status_code == 200
    assert type(response.json()) == list


def test_create_worker_valid():
    response = client.post('/workers', json={
        'name': 'danny_operator',
        'role': 'operator',
    })
    response_obj = response.json()
    assert response.status_code == 201


def test_create_worker_duplicate_name():
    response = client.post('/workers', json={
        'name': 'danny_operator',
        'role': 'operator',
    })
    response_obj = response.json()
    assert response.status_code == 500
    assert 'detail' in response_obj
    assert 'duplicate worker record found' in response_obj['detail']


def test_create_worker_invalid_role():
    response = client.post('/workers', json={
        'name': 'danny_foreman',
        'role': 'foreman',
    })
    response_obj = response.json()
    assert response.status_code == 422
    assert 'detail' in response_obj and len(response_obj['detail']) > 0
    assert 'value is not a valid enumeration member' in response_obj['detail'][0]['msg']
    

def test_get_worker_by_id_valid_id():
    response = client.get('/workers/1')
    assert response.status_code == 200
    assert type(response.json()) == dict


def test_get_worker_by_id_invalid_id():
    response = client.get('/workers/0')
    response_obj = response.json()
    assert response.status_code == 400
    assert response_obj['detail'] == 'worker not found'


def test_get_worker_by_name_valid():
    response = client.get('/workers/name/danny_operator')
    assert response.status_code == 200
    assert type(response.json()) == dict


def test_get_worker_by_name_invalid():
    response = client.get('/workers/name/nullbyte')
    response_obj = response.json()
    assert response.status_code == 400
    assert response_obj['detail'] == 'worker not found'


def test_associate_worker_with_farm_valid():
    response = client.post('/workers/1/farm/1/associate')
    assert response.status_code == 201


def test_associate_worker_with_farm_duplicate_insert():
    response = client.post('/workers/1/farm/1/associate')
    response_obj = response.json()
    assert response.status_code == 500
    assert 'detail' in response_obj
    assert 'association already exists' in response_obj['detail']


def test_reset_db():
    response = client.get('/provision')
    assert response.status_code != 403
