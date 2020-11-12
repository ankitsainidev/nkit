from typer.testing import CliRunner

from nkit import __version__
from nkit.main import app

runner = CliRunner()


def test_version():
    assert __version__ == '0.1.1'


def test_save():
    output = runner.invoke(app, ["note", "__test some note"])
    assert output.exit_code == 0
    assert b"success" in output.stdout_bytes.lower()

    output = runner.invoke(app, ["notes", "show", "--limit", "1"])
    assert output.exit_code == 0
    assert b"__test some note" in output.stdout_bytes.lower()

    # TODO: remove even if test fails
    output = runner.invoke(app, ["notes", "show","--id", "--limit", "1"])
    note_id = output.stdout_bytes.split(b" ")[0].decode("utf-8")
    output = runner.invoke(app, ["notes", "remove", str(note_id)])
    assert output.exit_code == 0

    output = runner.invoke(app, ["notes", "show", "--id", "--limit", "1"])
    assert output.exit_code == 0
    assert note_id.encode("utf-8") not in output.stdout_bytes.lower()
