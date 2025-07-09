class _DummyWidget:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        def _(*args, **kwargs):
            pass
        return _

def __getattr__(name):
    return _DummyWidget

