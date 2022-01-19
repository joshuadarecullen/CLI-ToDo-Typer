"""This module provides the RP To-Do CLI."""
# rptodo/cli.py

from typing import Optional

import typer

from rptodo import __app_name__, __version__

# creates a typer application
app = typer.Typer()

# prints app name and version then exits
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

# main as a typer callback decorator
@app.callback()
def main(
    # defines version, which is of type Optional[bool].
    # This means it can be either of bool or None type.
    # The version argument defaults to a typer.Option object,
    # which allows you to create command-line options in Typer.

    # passes None as the first argument to the initializer of Option.
    # This argument is required and supplies the option’s default value.

    # set the command-line names for the version option: -v and --version.
    # attaches a callback function, _version_callback(), to the version option,
    # which means that running the option automatically calls the function.

    # sets the is_eager argument to True. This argument tells 
    # Typer that the version command-line option has precedence 
    # over other commands in the current application.
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
