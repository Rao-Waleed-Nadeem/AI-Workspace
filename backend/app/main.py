from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router
from app.routes.auth import router as auth_router
from app.routes.files import router as files_router
from fastapi.staticfiles import StaticFiles
from app.routes.memory import router as memory_router
from app.routes.images import router as images_router
from app.routes.speech import router as speech_router

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(memory_router)
app.include_router(images_router)
app.include_router(speech_router)

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

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)
