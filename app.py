from fastapi import Depends, FastAPI, APIRouter


from config.config import Settings, initiate_database

from routes.print_request import router as PrintRequestRouter
from routes.order import router as OrderRouter
from routes.auth import router as AuthRouter
from routes.register import router as RegisterRouter
from routes.analytic import router as AnalyticRouter
from routes.auth import get_current_client

root_path = Settings().MS_ROOT_PATH

temp = APIRouter()

app = FastAPI(
    title="Print Order Reception Service",
    description="Print Request and Orders Reception Service API",
    version="1.0",
    docs_url=root_path + "/docs",
    openapi_url=root_path + "/openapi.json",
)


app.include_router(router=temp, prefix=root_path)


@app.on_event("startup")
async def start_database():
    await initiate_database()


app.include_router(
    PrintRequestRouter,
    tags=["Print Requests"],
    dependencies=[Depends(get_current_client)],
    prefix=root_path,
)

app.include_router(
    OrderRouter,
    tags=["Orders"],
    dependencies=[Depends(get_current_client)],
    prefix=root_path,
)
app.include_router(
    AuthRouter,
    tags=["Auth"],
    prefix=root_path,
)
app.include_router(RegisterRouter, tags=["Auth"], prefix=root_path)
app.include_router(AnalyticRouter, tags=["Analytic"], prefix=root_path)
