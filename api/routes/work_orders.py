from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import parse_obj_as
import starlette.status as status
from datetime import datetime
from tzlocal import get_localzone
from delorean import Delorean

from tracker import route_prefix
from api.backend.models import WorkOrders, WorkerAssignments, WorkTasks, CropCalendars
from api.backend.schemas import WorkOrder, WorkerAssignment, WorkTask

work_order_routes = APIRouter(prefix=f'{route_prefix}/orders')


@work_order_routes.get('/tasks', response_model=List[WorkTask], tags=['Work Orders'])
async def get_all_tasks() -> List[WorkTask]:
    tasks = WorkTasks.select()   
    return [parse_obj_as(WorkTask, task) for task in tasks.dicts()]


@work_order_routes.get('/', response_model=List[WorkOrder], tags=['Work Orders'])
async def get_all_work_orders() -> List[WorkOrder]:
    orders = WorkOrders.select() # type: ignore    
    return [order for order in orders]


@work_order_routes.get('/{id}', response_model=WorkOrder, tags=['Work Orders'])
async def get_work_order_by_id(id: int) -> WorkOrder:
    order = WorkOrders.select().where(WorkOrders.id == id).get_or_none() # type: ignore
    if order:
        return parse_obj_as(WorkOrder, order)
    else:
        raise HTTPException(
            status_code=404, detail='work order not found'
        )


@work_order_routes.post('/', status_code=status.HTTP_201_CREATED, response_model=WorkOrder, tags=['Work Orders'])
async def create_work_order(data: WorkOrder) -> WorkOrder:  
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate farm submission'
        )
    
    orders = WorkOrders()
    modified_fields = {key:value for (key,value) in data.dict().items() if value is not None}  
    for key, val in modified_fields.items():
        setattr(orders, key, val)
    
    try:
        orders.save()
    except:
        raise HTTPException(
            status_code=500, detail='unable to create work order. error or duplicate'
        )
    return parse_obj_as(WorkOrder, orders)


# TODO: combine 'generate' and 'plan' routes
@work_order_routes.post('/{id}/generate', response_model=None, status_code=status.HTTP_201_CREATED, tags=['Work Orders'])
async def generate_assignments_for_work_order(id: int) -> None:
    order = WorkOrders.select().where(WorkOrders.id == id).get_or_none() # type: ignore
    if order:        
        work_task_ids = [int(task_id) for task_id in order.tasks.split(', ')]
        for task_id in work_task_ids:
            is_completed = WorkerAssignments.select().where(WorkerAssignments.work_order_id == id).where(WorkerAssignments.task_id == task_id).where(WorkerAssignments.completed == None) # type: ignore

            if is_completed.count() == 0:
                assignment = WorkerAssignments(started=datetime.now(), work_order_id=id, task_id=task_id, completed=False)
                assignment.save()
    else:
        raise HTTPException(
            status_code=404, detail='work order not found'
        )


@work_order_routes.put('/{id}/plan', status_code=status.HTTP_204_NO_CONTENT, tags=['Work Orders'])
async def generate_work_assignment_plan(id: int) -> None:
    order = WorkOrders.select().where(WorkOrders.id == id).get_or_none() # type: ignore
    if not order:
        raise HTTPException(
            status_code=404, detail='work order not found'
        )    
    
    calendars = CropCalendars.select().where(CropCalendars.crop_name == order.field.crop).get_or_none()
    assignments = WorkerAssignments.select().where(WorkerAssignments.work_order_id == id) # type: ignore

    for assignment in assignments:        
        if assignment.task.name == 'sow' or assignment.task.name == 'roll' or '2nd fertilizer' in assignment.task.name:
            assignment.month_assigned = calendars.sow_start
        elif 'sow weeding' in assignment.task.name:
            assignment.month_assigned = calendars.sow_start + 1
        elif 'lime' in assignment.task.name:
            assignment.month_assigned = calendars.harvest_end + 1
        elif 'harvest' in assignment.task.name:
            assignment.month_assigned = calendars.harvest_start
        elif '1st fertilizer' in assignment.task.name:
            assignment.month_assigned = calendars.harvest_start + 1
        elif 'harvest weeding' in assignment.task.name or 'till' in assignment.task.name:
            assignment.month_assigned = calendars.harvest_start + 1
        elif 'forage' in assignment.task.name:
            assignment.month_assigned = calendars.harvest_start - 1
        assignment.save()    


@work_order_routes.put('/{id}/complete', status_code=status.HTTP_204_NO_CONTENT, tags=['Work Orders'])
async def mark_order_completed(id: int) -> None:
    d = Delorean()
    order = WorkOrders.select().where(WorkOrders.id == id).get_or_none() # type: ignore
    if not order:
        raise HTTPException(
            status_code=404, detail='work order not found'
        )
    order.completed = d.datetime.strftime("%Y-%m-%d")
    order.save()
