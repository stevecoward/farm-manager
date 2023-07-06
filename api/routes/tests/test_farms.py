from typing import Any
from tracker import app
from fastapi import Depends
from fastapi.testclient import TestClient
from peewee import SqliteDatabase, Model, _ConnectionState
from contextvars import ContextVar

client = TestClient(app, base_url='http://127.0.0.1:8000')


# def test_init_db():
#     response = client.get('/provision')
#     assert response.status_code != 403


def test_get_all_farms():
    response = client.get('/farms')
    assert response.status_code == 200
    assert type(response.json()) == list


def test_create_farm_valid():
    response = client.post('/farms', json={
        'name': 'Dummy Farm',
        'map_id': 1,
    })
    response_obj = response.json()
    assert response.status_code == 201
    assert response_obj['name'] == 'Dummy Farm'


def test_create_farm_duplicate():
    response = client.post('/farms', json={
        'name': 'Dummy Farm',
        'map_id': 1,
    })
    response_obj = response.json()
    assert response.status_code == 500
    assert 'detail' in response_obj
    assert 'duplicate farm record found' in response_obj['detail']


def test_get_farm_by_id_valid_id():
    response = client.get('/farms/1')
    assert response.status_code == 200
    assert type(response.json()) == dict


def test_get_farm_by_id_invalid_id():
    response = client.get('/farms/0')
    response_obj = response.json()
    assert response.status_code == 404
    assert response_obj['detail'] == 'farm not found'


def test_modify_farm_name_valid():
    response = client.put('/farms/1', json={
        'name': 'Dummy Farm Renamed',
        'map_id': 1,
    })
    assert response.status_code == 204


def test_get_farm_fields_valid_farm():
    response = client.get('/farms/1/fields')
    response_obj = response.json()
    assert response.status_code == 200
    assert type(response_obj) == list