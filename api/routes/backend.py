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
