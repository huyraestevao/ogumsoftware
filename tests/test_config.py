import os

from ogum.config import Settings


def test_settings_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "demo-proj")
    monkeypatch.setenv("DOCKER_REPO", "demo/repo")
    s = Settings()
    assert s.gcp_project_id == "demo-proj"
    assert s.docker_repo == "demo/repo"
