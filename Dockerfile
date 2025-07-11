FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install voila pytest-cov ruff scipy scikit-learn pyvista
RUN pip install fastapi uvicorn[standard] pydantic

COPY . .

EXPOSE 8866
