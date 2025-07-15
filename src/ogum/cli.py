"""Ogum command-line interface utilities."""

import click
from . import __version__
import diagnostics


@click.group()
@click.version_option(__version__)
def cli():
    """Ogum command-line interface."""


@cli.command()
def doctors():
    """Run environment diagnostics."""
    ok = diagnostics.run_diagnostics()
    if not ok:
        raise SystemExit(1)



if __name__ == "__main__":
    cli()
