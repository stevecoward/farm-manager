from typing import Any
from tracker import app
from fastapi import Depends
from fastapi.testclient import TestClient
from peewee import SqliteDatabase, Model, _ConnectionState
from contextvars import ContextVar

client = TestClient(app, base_url='http://127.0.0.1:8000')


def test_init_db():
    response = client.get('/provision')
    assert response.status_code != 403


def test_get_all_maps():
    response = client.get('/maps')
    assert response.status_code == 200
    assert type(response.json()) == list


def test_create_map_valid():
    response = client.post('/maps', json={
        'name': 'Test Map',
    })
    response_obj = response.json()
    assert response.status_code == 201
    assert response_obj['name'] == 'Test Map'


def test_create_map_duplicate():
    response = client.post('/maps', json={
        'name': 'Test Map',
    })
    response_obj = response.json()
    assert response.status_code == 500
    assert 'detail' in response_obj
    assert 'duplicate map record found' in response_obj['detail']


def test_get_map_by_id_valid_id():
    response = client.get('/maps/1')
    assert response.status_code == 200
    assert type(response.json()) == dict


def test_get_map_by_id_invalid_id():
    response = client.get('/maps/0')
    response_obj = response.json()
    assert response.status_code == 404
    assert response_obj['detail'] == 'map not found'


def test_modify_map_name_valid():
    response = client.put('/maps/1', json={
        'name': 'Test Map Renamed'
    })
    assert response.status_code == 204


def test_get_map_farms_valid_map():
    response = client.get('/maps/1/farms')
    response_obj = response.json()
    assert response.status_code == 200
    assert type(response_obj) == list