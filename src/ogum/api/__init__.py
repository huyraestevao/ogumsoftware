"""FastAPI application for Ogum."""

from fastapi import FastAPI
from .router import router

app = FastAPI(title="Ogum API")
app.include_router(router)

__all__ = ["app"]
