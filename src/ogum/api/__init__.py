"""FastAPI application for Ogum."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router
from .routes import router as services_router

app = FastAPI(title="Ogum API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openapi_tags = [
    {"name": "Master", "description": "Cálculo da curva mestra"},
    {"name": "FEM", "description": "Simulação elementos finitos"},
]
app.openapi_tags = openapi_tags
app.include_router(router)
app.include_router(services_router)

__all__ = ["app"]
