from typing import List
from fastapi import APIRouter, HTTPException
import starlette.status as status
from pydantic import parse_obj_as

from tracker import route_prefix
from api.backend.models import Fields, FieldYields
from api.backend.schemas import Field, FieldOptional


field_routes = APIRouter(prefix=f'{route_prefix}/fields')


@field_routes.get('/', response_model=List[Field], tags=['Fields'])
async def get_all_fields() -> List[Field]:
    fields = Fields.select(Fields.id, Fields.farm_id, Fields.name, Fields.acreage, Fields.yield_potential, Fields.crop, Fields.action, Fields.notes) # type: ignore
    return [parse_obj_as(Field, field) for field in fields]


@field_routes.get('/{id}', response_model=Field, tags=['Fields'])
async def get_field_by_id(id: int) -> Field:
    field = Fields.select(Fields.id, Fields.farm_id, Fields.name, Fields.acreage, Fields.yield_potential, Fields.crop, Fields.action, Fields.notes).where(Fields.id == id) # type: ignore
    if field.count() > 0:
        return parse_obj_as(Field, field.get())
    else:
        raise HTTPException(
            status_code=404, detail='field not found'
        )


@field_routes.post('/', status_code=status.HTTP_201_CREATED, response_model=Field, tags=['Fields'])
async def create_field(data: Field) -> Field:
    if not data.validate(data):
         raise HTTPException(
            status_code=400, detail='unable to validate field submission'
        )

    field = Fields()

    modified_fields = {key:value for (key,value) in data.dict().items() if value is not None}  
    try:
        for key, val in modified_fields.items():
            setattr(field, key, val)
        field.save()
    except:
        raise HTTPException(
            status_code=500, detail='duplicate field record found'
        )
    
    
    return parse_obj_as(Field, field)


@field_routes.put('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Fields'])
async def modify_field(id: int, data: FieldOptional) -> None:
    field = Fields.get_or_none(Fields.id == id) # type: ignore    
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate field modification'
        )
    
    if not field:
        raise HTTPException(
            status_code=404, detail='field not found'
        )

    modified_fields = {key:value for (key,value) in data.dict().items() if value is not None}  
    for key, val in modified_fields.items():
        setattr(field, key, val)
    field.save()


@field_routes.post('/{id}/yield', status_code=status.HTTP_201_CREATED, tags=['Fields'])
async def add_field_yield(id: int, data: dict) -> None:
    field = Fields.get_or_none(Fields.id == id) # type: ignore        
    if not field:
        raise HTTPException(
            status_code=404, detail='field not found'
        )
    
    field_yield = FieldYields.select().where(FieldYields.field_id == data['field_id']).where(FieldYields.assignment_id == data['assignment_id']) # type: ignore
    print(field_yield)
    field_yield = field_yield if field_yield.count() else FieldYields()
    for key, val in data.items():
        setattr(field_yield, key, val)
    field_yield.save()