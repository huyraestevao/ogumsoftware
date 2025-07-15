"""Ogum command-line interface utilities."""

import click
from . import __version__


@click.group()
@click.version_option(__version__)
def cli():
    """Ogum command-line interface."""


@cli.command()
def doctors():
    """Run environment diagnostics."""
    from .diagnostics import run_diagnostics  # hypotético

    run_diagnostics()


if __name__ == "__main__":
    cli()
