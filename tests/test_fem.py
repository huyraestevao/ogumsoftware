import importlib
import pytest

import ogum.fem_interface as fem


def test_fem_stub():
    if importlib.util.find_spec("fenicsx") is None:
        with pytest.raises(ModuleNotFoundError):
            fem.create_unit_mesh(1.0)
    else:
        fem.create_unit_mesh(1.0)
