# import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})
route_prefix = ''

from api.routes.backend import base_routes
from api.routes.farms import farm_routes
from api.routes.fields import field_routes
from api.routes.workers import worker_routes
from api.routes.work_orders import work_order_routes
from api.routes.work_assignments import work_assignment_routes
from api.routes.maps import map_routes

app.include_router(base_routes)
app.include_router(farm_routes)
app.include_router(field_routes)
app.include_router(worker_routes)
app.include_router(work_order_routes)
app.include_router(work_assignment_routes)
app.include_router(map_routes)

app.openapi_schema = get_openapi(
       title="FS22 Farm and Field Manager",
       version="0.1",
       routes=app.routes,
   )

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)