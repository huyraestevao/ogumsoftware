from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gcp_project_id: str = Field(..., env="GCP_PROJECT_ID")
    gcp_region: str = Field("southamerica-east1")
    docker_repo: str = Field(..., env="DOCKER_REPO")



__all__ = ["Settings"]
