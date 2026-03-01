import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.api.dreams import router as dreams_router
from backend.api.analysis import router as analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Dreamscape API",
    description="AI Dream Journal & Surrealist Film Generator",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dreams_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "dreamscape-backend"}
