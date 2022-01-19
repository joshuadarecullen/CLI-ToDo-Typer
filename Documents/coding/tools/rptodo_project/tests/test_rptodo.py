# tests/test_rptodo.py

from typer.testing import CliRunner

from rptodo import __app_name__, __version__, cli

runner = CliRunner()

# unit testing
def test_version():
    result = runner.invoke(cli.app, ["--version"])

    # asserts that the application’s exit code (result.exit_code) 
    # is equal to 0 to check that the application ran successfully.
    assert result.exit_code == 0

    # asserts that the application’s version is present in the standard output,
    # which is available through result.stdout.
    assert f"{__app_name__} v{__version__}\n" in result.stdout




# Typer’s CliRunner is a subclass of Click’s CliRunner.
# Therefore, its .invoke() method returns a Result object,
# which holds the result of running the CLI application with 
# the target arguments and options. Result objects provide several useful 
# attributes and properties, including the application’s exit 
# code and standard output. Take a look at the class documentation for more details.

