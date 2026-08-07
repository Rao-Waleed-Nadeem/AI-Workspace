from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router
from app.routes.auth import router as auth_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)

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
