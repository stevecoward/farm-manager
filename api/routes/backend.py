from typing import List
from fastapi import APIRouter, HTTPException
import starlette.status as status

from tracker import route_prefix
from api.backend import db
from api.backend.models import Farms, Fields
from api.backend.models import Workers, WorkerAssignments
from api.backend.models import WorkerFarms, WorkTasks, WorkOrders
from api.backend.models import GameConfig, CropCalendars, FieldYields
from api.backend.models import Maps
from api.backend.schemas import CropCalendar, WorkTask


base_routes = APIRouter(prefix=f'{route_prefix}/backend')


@base_routes.get('/provision', include_in_schema=False)
def provision_db():
    try:        
        db.connect()
        db.drop_tables([Farms, Fields, Workers, WorkerAssignments, WorkerFarms, WorkTasks, WorkOrders, GameConfig, CropCalendars, FieldYields, Maps])
        db.create_tables([Farms, Fields, Workers, WorkerAssignments, WorkerFarms, WorkTasks, WorkOrders, GameConfig, CropCalendars, FieldYields, Maps])
    except Exception as e:
        raise HTTPException(
            status_code=403, detail="failed to provision backend database"
        )


@base_routes.post('/calendars', status_code=status.HTTP_201_CREATED, response_model=List[CropCalendar], tags=['Backend'])
async def create_crop_calendars(data: List[CropCalendar]) -> List[CropCalendar]:    
    calendars = []
    for calendar in data:
        try:
            calendar = CropCalendars(**calendar.dict())
            calendar.save()
            calendars.append(calendar)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail='duplicate calendar record found'
            )
    
    return calendars


@base_routes.post('/worktasks', status_code=status.HTTP_201_CREATED, response_model=List[WorkTask], tags=['Backend'])
async def create_work_tasks(data: List[WorkTask]) -> List[WorkTask]:    
    worktasks = []
    for worktask in data:
        try:
            worktask = WorkTasks(**worktask.dict())
            worktask.save()
            worktasks.append(worktask)
        except:
            raise HTTPException(
                status_code=500, detail='duplicate work task record found'
            )
    
    return worktasks