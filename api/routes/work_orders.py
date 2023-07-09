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


class CalendarAssignments():
    def __init__(self, field_id: int, field_crop: str, calendars: CropCalendars, assignments: WorkerAssignments) -> None:
        self.field_id = field_id
        self.field_crop = field_crop
        self.calendars = {
            'sow_start': calendars.sow_start,
            'sow_end': calendars.sow_end,
            'harvest_start': calendars.harvest_start,
            'harvest_end': calendars.harvest_end,
            'forage_start': (calendars.harvest_start - 1),
            'forage_end': (calendars.harvest_end - 1)
        }
        self.forage_months = [3, 5, 7, 9, 11]
        self.assignments = assignments
    

    def check_completed_assignments_by_month(self, assignment: WorkTasks):
        for month in self.forage_months:
            results = WorkerAssignments.select()\
                .where(WorkerAssignments.completed == 0)\
                .where(WorkerAssignments.month_assigned == month)\
                .where(WorkerAssignments.task_id == assignment.task_id)
            if results.count() == 0:
                assignment.month_assigned = month
                assignment.save()
                return


    def calculate_for_grassland(self):
        for assignment in self.assignments:
            self.check_completed_assignments_by_month(assignment)


    def calculate_for_field(self):
            tasks = WorkTasks.select()
            for assignment in self.assignments:
                if assignment.task.group == 'pre_sow':
                    assignment.month_assigned = self.calendars['sow_start'] - 1
                elif assignment.task.group == 'sow':
                    assignment.month_assigned = self.calendars['sow']
                elif assignment.task.group == 'post_sow':
                    assignment.month_assigned = self.calendars['sow_start'] + 1
                elif assignment.task.group == 'forage':
                    assignment.month_assigned = self.calendars['forage_start']
                elif assignment.task.group == 'harvest':
                    assignment.month_assigned = self.calendars['harvest_start']
                elif assignment.task.group == 'post_harvest':
                    assignment.month_assigned = self.calendars['harvest_end']
                assignment.save()


    def generate(self):
        if self.field_crop == 'grass':
            self.calculate_for_grassland()
        else:
            self.calculate_for_field()


@work_order_routes.put('/{id}/plan', status_code=status.HTTP_204_NO_CONTENT, tags=['Work Orders'])
async def generate_work_assignment_plan(id: int) -> None:
    order = WorkOrders.select().where(WorkOrders.id == id).get_or_none() # type: ignore
    if not order:
        raise HTTPException(
            status_code=404, detail='work order not found'
        )    
    
    calendars = CropCalendars.select().where(CropCalendars.crop_name == order.field.crop).get_or_none()
    assignments = WorkerAssignments.select().where(WorkerAssignments.work_order_id == id) # type: ignore

    # TODO: break out of api call into own
    def check_existing(field_id: int, task_id: int, month: int):
        exists_for_assigned_month = WorkerAssignments.select()\
            .join(WorkOrders).where(WorkerAssignments.work_order_id == WorkOrders.id)\
            .where(WorkerAssignments.month_assigned == month)\
            .where(WorkerAssignments.task_id == task_id)\
            .where(WorkOrders.field_id == field_id)\
            .where(WorkerAssignments.completed == 0)
        return exists_for_assigned_month.count() > 0
    
    calendar_assignments = CalendarAssignments(order.field_id, order.field.crop, calendars, assignments)
    calendar_assignments.generate()


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
