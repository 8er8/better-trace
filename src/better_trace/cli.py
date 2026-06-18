import typer
import runpy
import sys

from . import initialize

app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    script: str,
    show_locals: bool = False,
    log_exceptions: bool = False,
    debugger: bool = False,
    mode: str = "verbose",
    theme: str = "monokai",
    background_color: str = "default",
):
    initialize(
        show_locals=show_locals,
        log_exceptions=log_exceptions,
        debugger=debugger,
        mode=mode,
        theme=theme,
        background_color=background_color,
    )

    if "--" in sys.argv:
        idx = sys.argv.index("--")
        script_args = sys.argv[idx + 1 :]
    else:
        script_args = []

    sys.argv = [script] + script_args
    runpy.run_path(script, run_name="__main__")


@app.command()
def demo():
    from . import demo

    demo()
