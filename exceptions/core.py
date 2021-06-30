from starlette.responses import JSONResponse
from fastapi import HTTPException, status
from fastapi import Request
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)


class CoreExceptionBase(Exception):
    def __init__(self, status_code: int, message: str):
        self.exception = self.__class__.__name__
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return (
            f"<Exception {self.exception} - "
            + f"status_code={self.status_code} - context={self.message}>"
        )


class CoreException(object):
    class NotFound(CoreExceptionBase):
        def __init__(self, message: str = "Not Found"):
            """
            Item Not found
            """
            status_code = HTTP_404_NOT_FOUND
            CoreExceptionBase.__init__(self, status_code, message)

    class UniqueViolationError(CoreExceptionBase):
        def __init__(self, message: str = "Already exist"):
            """
            Item Already exist
            """
            status_code = HTTP_422_UNPROCESSABLE_ENTITY
            CoreExceptionBase.__init__(self, status_code, message)


async def psql_not_unique(request, exc):
    response = {"message": "Document is not unique"}
    return JSONResponse(status_code=HTTP_409_CONFLICT, content=response)


async def exception_handler(request: Request, exc: CoreExceptionBase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "exception": exc.exception,
            "message": exc.message,
        },
    )
