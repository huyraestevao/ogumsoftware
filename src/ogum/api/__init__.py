"""FastAPI application for Ogum."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router

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

__all__ = ["app"]
