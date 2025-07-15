import importlib
import os
import tempfile
from unittest.mock import Mock

import pytest

from ogum.mesh_generator import generate_mesh


def test_generate_mesh_runs_or_errors(tmp_path, monkeypatch):
    try:
        importlib.import_module("gmsh")
    except Exception:
        with pytest.raises(ModuleNotFoundError):
            generate_mesh(1.0, 2.0, 0.5, 1)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".msh", delete=False)
        tmp.close()
        mock = Mock(return_value=tmp)
        monkeypatch.setattr(tempfile, "NamedTemporaryFile", mock)
        path = generate_mesh(0.2, 1.0, 0.1, 1)
        assert path == tmp.name
        assert os.path.isfile(path)
        assert path.endswith(".msh")
        os.remove(path)
