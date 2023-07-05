from typing import Any, List, Union, Optional
import peewee
from pydantic import BaseModel, ValidationError, validator
from pydantic.utils import GetterDict
from datetime import date, datetime
from api.backend.enums import FieldsCropEnum, FieldsActionEnum
from api.backend.enums import WorkersRoleEnum


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):        
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class Farm(BaseModel):
    id: Optional[int]
    name: Optional[str]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class Field(BaseModel):
    id: Optional[int]
    name: str
    acreage: float
    yield_potential: float
    crop: FieldsCropEnum
    action: FieldsActionEnum
    notes: Union[str, None] = None
    farm_id: int
    farm: Optional[Farm]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict
        arbitrary_types_allowed = True


class FieldOptional(BaseModel):
    name: Optional[str]
    acreage: Optional[float]
    yield_potential: Optional[float]
    crop: Optional[FieldsCropEnum]
    action: Optional[FieldsActionEnum]
    notes: Union[str, None] = None
    farm_id: int
    farm: Optional[Farm]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class WorkTask(BaseModel):
    id: Optional[int]
    name: str
    category: str


class Worker(BaseModel):
    id: Optional[int]
    name: str
    role: WorkersRoleEnum
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class WorkerFarm(BaseModel):
    id: Optional[int]
    name: str
    role: WorkersRoleEnum
    farms: List[dict]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class WorkerAssignment(BaseModel):
    started: Optional[date]
    work_order_id: int
    task_id: int
    completed: bool
    notes: Optional[str]
    month_assigned: int
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class WorkerAssignmentFilter(BaseModel):
    property: str
    value: str
    hide_completed: Optional[bool] = False

    @validator('property')
    def is_accepted_filter_property(cls, v):
        assert v in ['worker_id', 'farm_id', 'field_id', 'task_name', 'completed', 'work_order_id', 'due'], \
            'filter property must be one of the following: worker_id, farm_id, field_id, task_name, completed, work_order_id, due'
        return v


    @validator('value')
    def is_valid_value(cls, v, values, **kwargs):
        if 'property' in values:
            if values['property'] == 'completed':
                assert int(v) in [0, 1], 'completed should be either 0 or 1'
            if values['property'] == 'task_name':
                assert v in ['spread fertilizer', 'till', 'sow', 'roll', 'hoe, weed, or spread herbicide', 'harvest or forage', 'spread lime'], \
                'invalid task name'
        return v


class WorkerAssignmentFilterResult(BaseModel):
    worker_id: int
    worker_name: str
    worker_role: str
    farm_id: int
    farm_name: str
    field_id: int
    field_name: str
    task_name: str
    task_category: str
    assignment_id: int
    month_assigned: int
    started: datetime
    completed: bool


class WorkOrder(BaseModel):
    id: Optional[int]
    created: date
    farm_id: int
    farm: Optional[Farm]
    field_id: int
    field: Optional[Field]
    worker_id: int
    worker: Optional[Worker]
    tasks: str
    completed: Optional[datetime]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class FieldYield(BaseModel):
    field_id: int
    assignment_id: int
    amount_yield: float


class WorkerAssignmentOptional(BaseModel):
    started: Optional[date]
    work_order_id: Optional[int]
    task_id: Optional[int]
    completed: Optional[bool]
    notes: Optional[str]
    month_assigned: Optional[int]
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict