from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from asyncpg.exceptions import UniqueViolationError

from config.database import init_tables

from exceptions.request_exceptions import http_exception_handler, request_validation_exception_handler
from exceptions.core import CoreExceptionBase, exception_handler, psql_not_unique

from routers import workspace, state

app = FastAPI()
app.include_router(workspace.router)
app.include_router(state.router)

@app.on_event("startup")
async def startup():
    await init_tables()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)

@app.exception_handler(CoreExceptionBase)
async def custom_exception_handler(request, e):
    return await exception_handler(request, e)

@app.exception_handler(UniqueViolationError)
async def custom_psql_not_unique(request, e):
    return await psql_not_unique(request, e)
