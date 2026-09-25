from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router
from app.routes.auth import router as auth_router
from app.routes.files import router as files_router
from fastapi.staticfiles import StaticFiles
from app.routes.memory import router as memory_router
from app.routes.images import router as images_router
from app.routes.speech import router as speech_router
from app.routes.text_to_speech import (
    router as text_to_speech_router,
)
from app.core.logging_config import configure_logging
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)

from app.core.errors import AppError
from app.core.error_handlers import (
    app_error_handler,
    database_error_handler,
    http_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

configure_logging()

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; frame-ancestors 'none';"
    )
    return response

app.add_middleware(
    RequestLoggingMiddleware,
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(text_to_speech_router)
app.include_router(files_router)
app.include_router(memory_router)
app.include_router(images_router)
app.include_router(speech_router)

app.add_exception_handler(
    AppError,
    app_error_handler,
)

app.add_exception_handler(
    HTTPException,
    http_error_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    SQLAlchemyError,
    database_error_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_error_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Hello AI Workspace"
    }

# app.mount(
#     "/uploads",
#     StaticFiles(directory="uploads"),
#     name="uploads",
# )
