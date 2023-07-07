import click
from typing import Union
from requests.models import Response
from tables import FarmsTable, FarmFieldsTable, MapsTable
from console import runner, console


@click.group()
def entry_farms():
    pass


@entry_farms.command()
def get_farms() -> Union[Response, None]:    
    response = runner.call('/farms', 'GET', 400, 'unable to locate farms')
    if response:
        FarmsTable(response.json(), print=True)


# @entry_farms.command()
@click.argument('farm_id')
def get_farm_by_id(farm_id: int):
    response = runner.call(f'/farms/{farm_id}', 'GET', 400, 'unable to locate farm')
    if response:        
        FarmsTable(response.json(), print=True)


@entry_farms.command()
@click.argument('farm_id')
def get_farm_fields(farm_id: int) -> Union[Response, None]:
    response = runner.call(f'/farms/{farm_id}/fields', 'GET', 400, 'unable to get fields for farm')    
    if response:        
        FarmFieldsTable(response.json(), print=True)


@entry_farms.command()
@click.option('--name', '-n', prompt='Farm Name')
def create_farm(name: str):
    response = runner.call('/maps', 'GET', 400, 'unable to fetch maps')
    MapsTable(response.json(), print=True)
    
    chosen_map_id = input('Select a map ID: ')
    print('')

    response = runner.call(f'/farms/', 'POST', 500, 'unable to create farm', {
        'name': name,
        'map_id': chosen_map_id,
    })
    if response:
        FarmsTable(response.json(), print=True)


# @entry_farms.command()
@click.argument('farm_id')
@click.option('--name', '-n', prompt='Farm Name')
def update_farm(farm_id: int, name: str):
    response = runner.call(f'/farms/{farm_id}', 'PUT', 500, 'unable to modify farm', {
        'name': name
    })
    
    if response and response.status_code == 204:
        get_farm_by_id([farm_id])
