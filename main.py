from sys import prefix
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from asyncpg.exceptions import UniqueViolationError
from config.database import init_tables
from config.settings import settings, app_env
from exceptions.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi_plugins import redis_plugin
from exceptions.core import CoreExceptionBase, exception_handler, psql_not_unique
from routers import workspace, state, module, resource, healthz
import uvicorn

url_prefix = settings.URL_PREFIX

app = FastAPI(
    title="tfSpanner",
    description="Create and manage terraform resources",
    version="0.0.1",
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.OPENAPI_DOC_URL,
    redoc_url=settings.OPENAPI_REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspace.router, prefix=url_prefix)
app.include_router(state.router, prefix=url_prefix)
app.include_router(module.router, prefix=url_prefix)
app.include_router(resource.router, prefix=url_prefix)
app.include_router(healthz.router, prefix=url_prefix)


@app.on_event("startup")
async def startup():
    await init_tables()
    await redis_plugin.init_app(app, config=settings)
    await redis_plugin.init()


@app.on_event("shutdown")
async def close_redis():
    await redis_plugin.terminate()


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


if __name__ == "__main__":
    config = {
        "log_level": "debug",
        "host": settings.SERVER_HOST,
        "port": settings.SERVER_PORT,
    }
    if app_env == "development":
        config["reload"] = True
    uvicorn.run("main:app", **config)
