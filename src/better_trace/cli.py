import typer
import runpy
import sys

from . import initialize, __version__

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the CLI version and exit.",
    ),
):
    pass


@app.command()
def run(
    script: str,
    show_locals: bool = False,
    log_exceptions: bool = False,
    debugger: bool = False,
    mode: str = "verbose",
    theme: str = "monokai",
    background_color: str = "default",
    use_config: bool = False,
):
    initialize(
        show_locals=show_locals,
        log_exceptions=log_exceptions,
        debugger=debugger,
        mode=mode,
        theme=theme,
        background_color=background_color,
        use_config=use_config,
    )

    if "--" in sys.argv:
        idx = sys.argv.index("--")
        script_args = sys.argv[idx + 1 :]
    else:
        script_args = []

    sys.argv = [script] + script_args
    try:
        runpy.run_path(script, run_name="__main__")
    except FileNotFoundError:
        typer.echo(f"File {script} does not exist.")


@app.command()
def demo():
    from . import demo

    demo()
