from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config.database import init_tables
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.request_exceptions import http_exception_handler, request_validation_exception_handler

from routers import workspace

init_tables()

app = FastAPI()
app.include_router(workspace.router)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)

@app.get("/")
async def root():
    return {"message": "Hello World"}

    
