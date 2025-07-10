"""Lightweight stand-ins for IPython display helpers."""


def display(*args, **kwargs):
    """No-op replacement for :func:`IPython.display.display`."""
    pass


class HTML(str):
    """Dummy HTML container used in tests."""
    pass


def clear_output(*args, **kwargs):
    """No-op replacement for :func:`IPython.display.clear_output`."""
    pass
