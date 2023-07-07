import click
from tables import FarmFieldsTable
from console import runner, console


@click.group()
def entry_fields():
    pass


@entry_fields.command()
def get_fields():
    response = runner.call('/fields', 'GET', 400, 'unable to locate fields')
    if response:
        FarmFieldsTable(response.json(), print=True)


# @entry_fields.command()
@click.argument('id')
def get_field_by_id(id: int):
    response = runner.call(f'/fields/{id}', 'GET', 400, 'unable to locate field')    
    if response:        
        FarmFieldsTable(response.json(), print=True)


# @entry_fields.command()
@click.argument('id')
@click.argument('farm_id')
@click.option('--size', '-s', type=float)
@click.option('--yield_potential', '-y', type=float)
@click.option('--crop', '-c', type=click.Choice([
    'wheat', 'barley', 'canola', 'oat', 'corn', 
    'sunflowers', 'soybeans', 'potatoes', 'sugar_beet', 
    'sugarcane', 'cotton', 'sorghum', 'grapes', 'olives', 
    'grass', 'oilseed_radish'
]))
@click.option('--action', '-a', type=click.Choice(['harvest', 'forage']))
@click.option('--notes', '-n', type=str)
def update_field(id: int, farm_id: int, size: float, yield_potential: float, crop: str, action: str, notes: str):
    payload = {
        'farm_id': farm_id,
        'size': size,
        'yield_potential': yield_potential,
        'crop': crop,
        'action': action,
        'notes': notes
    }
    submitted_changes = {key:value for (key,value) in payload.items() if value is not None}
    
    response = runner.call(f'/fields/{id}', 'PUT', 500, 'unable to modify field', submitted_changes)
    
    if response and response.status_code == 204:
        get_field_by_id([id])


@entry_fields.command()
@click.argument('farm_id')
@click.option('--name', type=str, prompt='Field Number')
@click.option('--size', '-s', type=float, prompt='Field Acreage')
@click.option('--yield_potential', '-y', type=float, prompt='Potential Yield')
@click.option('--crop', '-c', type=click.Choice([
    'wheat', 'barley', 'canola', 'oat', 'corn', 
    'sunflowers', 'soybeans', 'potatoes', 'sugar_beet', 
    'sugarcane', 'cotton', 'sorghum', 'grapes', 'olives', 
    'grass', 'oilseed_radish'
]), prompt='Crop')
@click.option('--action', '-a', type=click.Choice(['harvest', 'forage']), prompt='Intended Action')
@click.option('--notes', '-n', type=str, prompt='Field Notes')
def create_field(farm_id: int, name: str, size: float, yield_potential: float, crop: str, action: str, notes: str):
    payload = {
        'farm_id': farm_id,
        'name': name,
        'acreage': size,
        'yield_potential': yield_potential,
        'crop': crop,
        'action': action,
        'notes': notes
    }    
    
    response = runner.call(f'/fields/', 'POST', 500, 'unable to create field', payload)
    
    if response and response.status_code == 204:
        get_field_by_id([id])
