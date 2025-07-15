import os

from ogum.config import Settings


def test_settings_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "my-proj")
    monkeypatch.setenv("DOCKER_REPO", "docker/repo")
    s = Settings()
    assert s.gcp_project_id == "my-proj"
    assert s.docker_repo == "docker/repo"
