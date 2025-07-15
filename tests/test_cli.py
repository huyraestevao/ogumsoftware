from click.testing import CliRunner

from ogum.cli import cli


def test_doctors_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctors"])
    assert result.exit_code == 0
