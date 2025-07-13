FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y gmsh
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install voila pytest-cov ruff scipy scikit-learn pyvista
RUN pip install fastapi uvicorn[standard] pydantic

COPY . .

EXPOSE 8866
EXPOSE 8000
