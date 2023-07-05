from fastapi import APIRouter, HTTPException

from tracker import route_prefix
from api.backend import db
from api.backend.models import Farms, Fields
from api.backend.models import Workers, WorkerAssignments
from api.backend.models import WorkerFarms, WorkTasks, WorkOrders
from api.backend.models import GameConfig, CropCalendars, FieldYields


base_routes = APIRouter(prefix=route_prefix)


@base_routes.get('/provision', include_in_schema=False)
def provision_db():
    try:        
        db.connect()
        db.drop_tables([Farms, Fields, Workers, WorkerAssignments, WorkerFarms, WorkTasks, WorkOrders, GameConfig, CropCalendars, FieldYields])
        db.create_tables([Farms, Fields, Workers, WorkerAssignments, WorkerFarms, WorkTasks, WorkOrders, GameConfig, CropCalendars, FieldYields])
    except Exception as e:
        raise HTTPException(
            status_code=403, detail="failed to provision backend database"
        )


@base_routes.get('/init', include_in_schema=False)
def initialize_db_data():
    cropcalendars_data = [{
        'crop_name': 'corn',
        'sow_start': 4,
        'sow_end': 5,
        'harvest_start': 10,
        'harvest_end': 11,
    },{
        'crop_name': 'canola',
        'sow_start': 8,
        'sow_end': 9,
        'harvest_start': 7,
        'harvest_end': 8,
    },{
        'crop_name': 'wheat',
        'sow_start': 9,
        'sow_end': 10,
        'harvest_start': 7,
        'harvest_end': 8,
    },{
        'crop_name': 'barley',
        'sow_start': 9,
        'sow_end': 10,
        'harvest_start': 6,
        'harvest_end': 7,
    },{
        'crop_name': 'soybeans',
        'sow_start': 5,
        'sow_end': 6,
        'harvest_start': 10,
        'harvest_end': 11,
    },{
        'crop_name': 'grass',
        'sow_start': 3,
        'sow_end': 11,
        'harvest_start': 3,
        'harvest_end': 11,
    },{
        'crop_name': 'sugar_beet',
        'sow_start': 3,
        'sow_end': 4,
        'harvest_start': 10,
        'harvest_end': 11,
    },{
        'crop_name': 'sugarcane',
        'sow_start': 3,
        'sow_end': 4,
        'harvest_start': 10,
        'harvest_end': 11,
    },]
    worktasks_data = [{
        'name': 'spread 1st fertilizer',
        'category': 'field',
    },{
        'name': 'till',
        'category': 'field',
    },{
        'name': 'sow',
        'category': 'field',
    },{
        'name': 'roll',
        'category': 'field',
    },{
        'name': 'post sow weeding',
        'category': 'field',
    },{
        'name': 'harvest',
        'category': 'field',
    },{
        'name': 'spread lime',
        'category': 'field',
    },{
        'name': 'spread 2nd fertilizer',
        'category': 'field',
    },{
        'name': 'forage',
        'category': 'field',
    },{
        'name': 'post harvest weeding',
        'category': 'field',
    },{
        'name': 'mow',
        'category': 'grassland',
    },{
        'name': 'ted',
        'category': 'grassland',
    },{
        'name': 'wind row/rake',
        'category': 'grassland',
    },{
        'name': 'forage wagon',
        'category': 'grassland',
    },{
        'name': 'roll',
        'category': 'grassland',
    },{
        'name': 'bale',
        'category': 'grassland',
    },]
    
    for record in cropcalendars_data:
        try:
            calendar = CropCalendars(**record)
            calendar.save()
        except Exception as e:
            pass

    for record in worktasks_data:
        try:
            worktask = WorkTasks(**record)
            worktask.save()
        except Exception as e:
            pass