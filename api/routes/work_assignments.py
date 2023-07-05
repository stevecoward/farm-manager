from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import parse_obj_as
import starlette.status as status
from datetime import datetime

from tracker import route_prefix
from api.backend import db
from api.backend.models import WorkerAssignments, CropCalendars
from api.backend.schemas import WorkerAssignment, WorkerAssignmentFilter, WorkerAssignmentFilterResult, WorkerAssignmentOptional


work_assignment_routes = APIRouter(prefix=f'{route_prefix}/assignments')


@work_assignment_routes.post('/filter', response_model=List[WorkerAssignmentFilterResult], status_code=status.HTTP_200_OK, tags=['Work Assignments'])
async def filter_get_work_assignments(filter: List[WorkerAssignmentFilter]) -> List[WorkerAssignmentFilterResult]:  
    # TODO: use ORM
    query_sql = f"""SELECT 
	w.id AS 'worker_id', 
	w.name AS 'worker', 
	w.role,
    f.id AS 'farm_id',
    f.name AS 'farm_name',
    fi.id AS 'field_id',
    fi.name AS 'field_name',
    wt.name AS 'task_name',
    wt.category,
    wa.id AS 'assignment_id',
    wa.month_assigned,
    wa.started,
    wa.completed
FROM workerassignments wa
JOIN workorders wo ON wa.work_order_id = wo.id
JOIN worktasks wt ON wa.task_id = wt.id
JOIN farms f ON wo.farm_id = f.id
JOIN fields fi ON wo.field_id = fi.id
JOIN workers w ON wo.worker_id = w.id
_FILTER_CLAUSE_
"""
    filter_clauses = []
    for search_filter in filter:
        if search_filter.property == 'completed':
            filter_clauses.append(f'wa.completed == {int(search_filter.value)}')
        if search_filter.property == 'task_name':
            filter_clauses.append(f'wt.name == "{search_filter.value}"')
        if search_filter.property == 'worker_id':
            filter_clauses.append(f'w.id == {int(search_filter.value)}')
        if search_filter.property == 'work_order_id':
            filter_clauses.append(f'wo.id == {int(search_filter.value)}')
        if search_filter.property == 'farm_id':
            filter_clauses.append(f'f.id == {int(search_filter.value)}')
        if search_filter.property == 'field_id':
            filter_clauses.append(f'fi.id == {int(search_filter.value)}')
        if search_filter.property == 'due':
            filter_clauses.append(f'wa.month_assigned == {int(search_filter.value)}')
        if search_filter.hide_completed:
            filter_clauses.append(f'wa.completed == 0')
    
    filter_where = f'WHERE {filter_clauses[0]}'
    filter_and = ''
    for item in filter_clauses[1:]:
        filter_and += f'AND {item}'

    query_sql = query_sql.replace('_FILTER_CLAUSE_', f'{filter_where} {filter_and}')
    query = db.execute_sql(query_sql)
    results = []
    
    for record in query:
        worker_id, worker, role, farm_id, farm_name, field_id, field_name, task_name, category, assignment_id, month_assigned, started, completed = record
        result = WorkerAssignmentFilterResult(worker_id=worker_id, worker_name=worker, worker_role=role, farm_id=farm_id, \
                                                farm_name=farm_name, field_id=field_id, field_name=field_name, task_name=task_name, \
                                                task_category=category, assignment_id=assignment_id, month_assigned=month_assigned, started=started, completed=completed)
        results.append(result)
    
    return results


@work_assignment_routes.get('/', response_model=List[WorkerAssignment], tags=['Work Assignments'])
async def get_all_work_assignments() -> List[WorkerAssignment]:
    assignments = WorkerAssignments.select() # type: ignore    
    return [assignment for assignment in assignments]


@work_assignment_routes.get('/{id}', response_model=WorkerAssignment, tags=['Work Assignments'])
async def get_work_assignment_by_id(id: int) -> WorkerAssignment:
    assignment = WorkerAssignments.select().where(WorkerAssignments.id == id).get_or_none() # type: ignore
    if assignment:
        return parse_obj_as(WorkerAssignment, assignment)
    else:
        raise HTTPException(
            status_code=404, detail='work assignment not found'
        )


@work_assignment_routes.get('/work-order/{id}', response_model=List[WorkerAssignment], tags=['Work Assignments'])
async def get_work_assignment_by_work_order(id: int) -> List[WorkerAssignment]:
    assignments = WorkerAssignments.select().where(WorkerAssignments.work_order_id == id) # type: ignore
    return [assignment for assignment in assignments]


@work_assignment_routes.put('/{id}/complete', status_code=status.HTTP_204_NO_CONTENT, tags=['Work Assignments'])
async def mark_assignment_completed(id: int) -> None:
    assignment = WorkerAssignments.select().where(WorkerAssignments.id == id).get_or_none() # type: ignore
    if assignment:
        assignment.completed = True
        assignment.save()
    else:
        raise HTTPException(
            status_code=404, detail='work assignment not found'
        )


@work_assignment_routes.put('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Work Assignments'])
async def update_assignment(id: int, data: WorkerAssignmentOptional) -> None:
    assignment = WorkerAssignments.select().where(WorkerAssignments.id == id).get_or_none() # type: ignore
    if assignment:
        modified_fields = {key:value for (key,value) in data.dict().items() if value is not None}  
        for key, val in modified_fields.items():
            setattr(assignment, key, val)
        assignment.save()
    else:
        raise HTTPException(
            status_code=404, detail='work assignment not found'
        )
