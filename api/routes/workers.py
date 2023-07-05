from typing import List
from fastapi import APIRouter, HTTPException
import starlette.status as status
from pydantic import parse_obj_as
from peewee import fn, JOIN

from tracker import route_prefix
from api.backend.models import Workers, WorkerFarms
from api.backend.schemas import Worker, WorkerFarm


worker_routes = APIRouter(prefix=f'{route_prefix}/workers')


@worker_routes.get('/', response_model=List[Worker], tags=['Workers'])
async def get_all_workers() -> List[Worker]:
    workers = Workers.select(Workers.id, Workers.name, Workers.role)    
    return [worker for worker in workers]


@worker_routes.get('/{id}', response_model=WorkerFarm, tags=['Workers'])
async def get_worker_by_id(id: int) -> WorkerFarm:
    get_worker = Workers.select(Workers, WorkerFarms)\
        .join(WorkerFarms, JOIN.LEFT_OUTER)\
        .where(Workers.id == id) # type: ignore        
    worker_records = get_worker.get_or_none()    
    
    farms = []
    if worker_records:        
        farms = [{'id': record.workerfarms.farm.id, 'name': record.workerfarms.farm.name} for record in get_worker]
    
    if worker_records and Worker.validate(worker_records):
        return WorkerFarm(id=worker_records.id, name=worker_records.name, role=worker_records.role, farms=farms)
    
    raise HTTPException(
            status_code=400, detail='worker not found'
        )  


@worker_routes.get('/name/{name}', response_model=WorkerFarm, tags=['Workers'])
async def get_worker_by_name(name: str) -> WorkerFarm:    
    get_worker = Workers.select(Workers, WorkerFarms)\
        .join(WorkerFarms, JOIN.LEFT_OUTER)\
        .where(Workers.name == name) # type: ignore        
    worker_records = get_worker.get_or_none()    
    
    farms = []
    if worker_records:
        for record in get_worker:
            if hasattr(record, 'workerfarms'):
                farms.append({
                    'id': record.workerfarms.farm.id,
                    'name': record.workerfarms.farm.name,
                })

    if worker_records and Worker.validate(worker_records):
        return WorkerFarm(id=worker_records.id, name=worker_records.name, role=worker_records.role, farms=farms)
    
    raise HTTPException(
            status_code=400, detail='worker not found'
        )   


@worker_routes.post('/', status_code=status.HTTP_201_CREATED, response_model=Worker, tags=['Workers'])
async def create_worker(data: Worker) -> Worker:
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate worker submission'
        )

    try:
        worker = Workers(**data.dict())
        worker.save()
        return parse_obj_as(Worker, worker)
    except:
        raise HTTPException(
            status_code=500, detail='duplicate worker record found'
        )


@worker_routes.post('/{id}/farm/{farm_id}/associate', status_code=status.HTTP_201_CREATED, tags=['Workers'])
async def associate_with_farm(farm_id: int, id: int) -> None:    
    try:
        table = WorkerFarms(farm_id=farm_id, worker_id=id)    
        table.save()
    except:
        raise HTTPException(
            status_code=500, detail='association already exists'
        )
