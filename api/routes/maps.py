from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import parse_obj_as
import starlette.status as status

from tracker import route_prefix
from api.backend.models import Farms, Fields, Maps
from api.backend.schemas import Farm, Field, Map


map_routes = APIRouter(prefix=f'{route_prefix}/maps')


@map_routes.get('/', response_model=List[Map], tags=['Maps'])
async def get_all_maps() -> List[Map]:
    maps = Maps.select() # type: ignore
    return [map for map in maps]


@map_routes.get('/{id}', response_model=Map, tags=['Maps'])
async def get_map_by_id(id: int) -> Map:
    map = Maps.select(Maps.id, Maps.name).where(Maps.id == id).get_or_none() # type: ignore
    if map:
        return parse_obj_as(Map, map)
    else:
        raise HTTPException(
            status_code=404, detail='map not found'
        )


@map_routes.get('/{id}/farms', response_model=List[Farm], tags=['Maps'])
async def get_map_farms(id: int) -> List[Farm]:
    farms = Farms.select().join(Maps).where(Farms.map_id == Maps.id).where(Maps.id == id) # type: ignore  
    return [farm for farm in farms]


@map_routes.post('/', status_code=status.HTTP_201_CREATED, response_model=Map, tags=['Maps'])
async def create_map(data: Map) -> Map:  
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate map submission'
        )

    try:
        map = Maps(**data.dict())
        map.save()
        return parse_obj_as(Map, map)
    except:        
        raise HTTPException(
            status_code=500, detail='duplicate map record found'
        )


@map_routes.put('/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Maps'])
async def modify_map(id: int, data: Map) -> None:
    data.id = id    
    map = Maps.get_or_none(Maps.id == id) # type: ignore
    if not data.validate(data):
        raise HTTPException(
            status_code=400, detail='unable to validate map modification'
        )
    
    if not map:
        raise HTTPException(
            status_code=404, detail='map not found'
        )

    map = Maps(**data.dict())
    map.save()


    
