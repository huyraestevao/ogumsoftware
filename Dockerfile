FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install voila pytest-cov ruff scipy scikit-learn pyvista
RUN pip install fastapi uvicorn[standard] pydantic

COPY . .

EXPOSE 8866
ENTRYPOINT ["voila", "--no-browser", "--Voila.ip=0.0.0.0", "notebooks/FEM_example.ipynb"]
CMD ["uvicorn", "ogum.api:app", "--host", "0.0.0.0", "--port", "8000"]
