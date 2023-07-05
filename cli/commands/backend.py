import click
from console import runner, console
from tables import FarmsTable


@click.group()
def entry_backend():
    pass

@entry_backend.command()
def bootstrap():
    farms = ['Ligma Bales Co.', 'Hay Gurl Farms', 'Sweetbeetz Co-Op', 'Dr. Greenthumb\'s Growhouse']
    fields_ligma = [{
        'name': 'F23',
        'acreage': 5.92,
        'yield_potential': 110,
        'crop': 'barley',
        'action': 'harvest',
        'notes': 'used by hay gurl farms contractors'
    }, {
        'name': 'F24',
        'acreage': 6.37,
        'yield_potential': 122,
        'crop': 'wheat',
        'action': 'harvest',
        'notes': 'used by hay gurl farms contractors'
    }]
    fields_haygurl = [{
        'name': 'F1',
        'acreage': 25.32,
        'yield_potential': 112,
        'crop': 'corn',
        'action': 'forage',
        'notes': '',
    }, {
        'name': 'F10',
        'acreage': 6.87,
        'yield_potential': 105,
        'crop': 'grass',
        'action': 'forage',
        'notes': '',
    }, {
        'name': 'F11',
        'acreage': 5.71,
        'yield_potential': 111,
        'crop': 'grass',
        'action': 'forage',
        'notes': 'decom grass for soybeans next harvest'
    }]

    click.secho('Creating farm records...', fg='yellow')
    for farm in farms:
        response = runner.call(f'/farms/', 'POST', 500, 'unable to create farm', {
            'name': farm
        })
        if response:
            FarmsTable(response.json(), print=True)

    for field in fields_ligma:
        payload = {
            'farm_id': 1,
            'name': field['name'],
            'acreage': field['acreage'],
            'yield_potential': field['yield_potential'],
            'crop': field['crop'],
            'action': field['action'],
            'notes': field['notes']
        }
        
        response = runner.call(f'/fields/', 'POST', 500, 'could not create field', payload)
        
        if response and response.status_code == 204:
            # get_field_by_id([id])
            pass
    
    for field in fields_haygurl:
        payload = {
            'farm_id': 2,
            'name': field['name'],
            'acreage': field['acreage'],
            'yield_potential': field['yield_potential'],
            'crop': field['crop'],
            'action': field['action'],
            'notes': field['notes']
        }
        
        response = runner.call(f'/fields/', 'POST', 500, 'could not create field', payload)
        
        if response and response.status_code == 204:
            # get_field_by_id([id])
            pass