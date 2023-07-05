from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import parse_obj_as
import starlette.status as status

from tracker import route_prefix
from api.backend.models import Farms, Fields
from api.backend.schemas import Farm, Field


farm_routes = APIRouter(prefix=f'{route_prefix}/farms')


@farm_routes.get('/', response_model=List[Farm], tags=['Farms'])
async def get_all_farms() -> List[Farm]:
    farms = Farms.select(Farms.id, Farms.name) # type: ignore
    return [farm for farm in farms]


@farm_routes.get('/{id}', response_model=Farm, tags=['Farms'])
async def get_farm_by_id(id: int) -> Farm:
    farm = Farms.select(Farms.id, Farms.name).where(Farms.id == id).get_or_none() # type: ignore
    if farm:
        return parse_obj_as(Farm, farm)
    else:
        raise HTTPException(
            status_code=404, detail='farm not found'
        )


@farm_routes.get('/{id}/fields', response_model=List[Field], tags=['Farms'])
async def get_farm_fields(id: int) -> List[Field]:
    fields = Fields.select().join(Farms).where(Fields.farm_id == Farms.id).where(Farms.id == id) # type: ignore  
    return [field for field in fields]


@farm_routes.post('/', status_code=status.HTTP_201_CREATED, response_model=Farm, tags=['Farms'])
async def create_farm(data: Farm) -> Farm:  
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate farm submission'
        )

    try:
        farm = Farms(**data.dict())
        farm.save()
        return parse_obj_as(Farm, farm)
    except:        
        raise HTTPException(
            status_code=500, detail='duplicate farm record found'
        )


@farm_routes.put('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Farms'])
async def modify_farm(id: int, data: Farm) -> None:
    data.id = id    
    farm = Farms.get_or_none(Farms.id == id) # type: ignore
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate farm modification'
        )
    
    if not farm:
        raise HTTPException(
            status_code=404, detail='farm not found'
        )

    farm = Farms(**data.dict())
    farm.save()


    
