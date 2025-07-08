import importlib, pytest
@pytest.mark.parametrize('m', [
    'ogum.core', 'ogum.ogum64', 'ogum.ogum72', 'ogum.ogum80'
])
def test_imports(m):
    assert importlib.import_module(m)
