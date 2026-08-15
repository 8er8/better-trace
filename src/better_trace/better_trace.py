from types import TracebackType
from warnings import warn
import sys
import traceback
import threading
import builtins
import logging
import difflib
import tomllib

_has_rich: bool = True


try:
    from rich import print
except ModuleNotFoundError:
    warn(
        "Download rich to get colors and syntax highlighting",
        RuntimeWarning,
        stacklevel=4,
    )
    _has_rich = False

__all__ = ["initialize", "demo", "revert"]
logging.basicConfig(
    filename="crash.log",
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.ERROR,
)
from ._formatter import (
    print_exception_group,
    render_syntax_error,
    print_debug,
    print_verbose,
    print_context,
    print_compact,
    print_minimal,
)
from ._config import config

#  ╭────────────────╮
#  │  better-trace  │
#  ╰────────────────╯
#     better-trace
#          ❤
#       unicode
# Copyright (c) 2026 Adamya Mondal
#
# A colorful traceback formatter for Python
# Contributors — Adamya (me!)
# Developers — Adamya (me!)
# License — MIT


class InvalidModeWarning(Warning):
    pass


def _initialize_mode(mode: str) -> str:
    """
    _initialize_mode is used to initialize the mode by taking the mode name given by the user.
    If the mode doesn't exist, it would first try to get the first match usinfg difflib.
    If there was no match, it would fallback to context mode
    Args:
        mode (str): The mode given by the user
    Returns:
        mode (if mode exists), match[0] (if there was a match), 'context' (if there wasn't any match)
    ## Used by:
        initialize
    ## Notes:
        It is an internal function, so don't call it
    """
    if mode in _MODES:
        return mode
    match = difflib.get_close_matches(mode, _MODES, n=1)
    if match:
        warn(
            f"Invalid mode: {mode}. Did you mean {match[0]}? Falling back to closest match",
            InvalidModeWarning,
            stacklevel=3,
        )
        return match[0]
    else:
        warn(
            f"Invalid mode: {mode}. Falling back to 'context'",
            InvalidModeWarning,
            stacklevel=3,
        )
    return "context"


_MODES = {
    "debug": print_debug,
    "verbose": print_verbose,
    "context": print_context,
    "compact": print_compact,
    "minimal": print_minimal,
}


def _print_tb(
    title: str,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    tb: TracebackType | None,
    exceptgroup: bool = False,
) -> None:
    """
    _print_tb() is used to print the traceback with a custom title
    Args:
        title (str): The custom title to print the header with
        exc_type (Type[BaseException] | None): The type of the exception
        exc (BaseException | None): The instance of the exception
        tb (TracebackType | None): The traceback object
    Returns:
        None
    Used By:
        _customhook()
    Notes:
        This function is intended to be an internal helper, and it is not meant to be called directly
    """
    old_tb = tb
    tb_items = list(traceback.walk_tb(tb))
    frames = traceback.StackSummary.extract(tb_items)
    for frame, (_, lineno) in zip(frames, tb_items):
        frame.lineno = lineno
    if not frames:
        if exceptgroup:
            if not _has_rich:
                print(
                    f"> {exc_type.__name__ or 'UnknownError'}: {str(exc) or '<no message provided>'}"
                )
            else:
                print(
                    f"[red]>[bold] {exc_type.__name__ or 'UnknownError'}[/bold]: {str(exc) or '<no message provided>'}[/red]"
                )
            return
        builtins.print("ERROR: No traceback available")
        builtins.print("Printing original traceback...")
        sys.__excepthook__(exc_type, exc, tb)
        return
    if config.mode == "verbose":
        _MODES["verbose"](title, frames, exc_type, exc, tb)
    elif config.mode == "debug":
        _MODES["debug"](title, frames, exc_type, exc, tb)
    else:
        _MODES[config.mode](frames, exc_type, exc, tb)

    if config.log_exceptions:
        if not _has_rich:
            print(f"Logging exception to crash.log...")
        else:
            print(f"[cyan][bold]Note[/bold]: Logging exception to crash.log...[/cyan]")
        logging.error("Unhandled exception", exc_info=(exc_type, exc, old_tb))


def _customhook(
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    tb: TracebackType | None,
) -> None:
    """
    _customhook() is used to display the custom traceback via initialize() with the help of _print_tb().
    Args:
        exc_type (Type[BaseException] | None): The type of the exception
        exc (BaseException | None): The instance of the exception
        tb (TracebackType | None): The traceback object
    Returns:
        None
    Used by:
        initialize()
    Notes:
        This function is internal, so don't call it directly
    """
    # what does【東方ボーカルMV】メイドノココロハアヤツリドール（Vo:あよ）【森羅万象公式】 even mean tbh
    try:
        if exc_type and issubclass(exc_type, KeyboardInterrupt):
            if not _has_rich:
                print(f"Keyboard Interrupt".center(50, "─"))
                print("The program was terminated by the user")
                print(
                    "Note: If you triggered it accidentally, note that Ctrl + C mean KeyboardInterrupt"
                )
            else:
                print("[yellow]Keyboard Interrupt[/yellow]".center(50, "─"))
                print("[yellow]The program was terminated by the user[/yellow]")
                print(
                    "[cyan]Note: [/cyan]If you triggered it accidentally, note that Ctrl + C means KeyboardInterrupt"
                )
            return
        if exc_type and issubclass(exc_type, SyntaxError):
            if tb is None and exc is not None:
                render_syntax_error(exc)
                return
        if isinstance(exc, ExceptionGroup):
            print_exception_group(exc, tb)
            return
        if exc and exc.__cause__:
            cause = exc.__cause__
            _print_tb("An error occurred", type(cause), cause, cause.__traceback__)
            if not _has_rich:
                print(
                    "\n────The above exception was the cause of the other exception below────\n"
                )
            else:
                print(
                    "\n────[red]The above exception was the cause of the other exception below[/red]────\n"
                )
            _print_tb("Another error occurred", exc_type, exc, tb)
        elif exc and exc.__context__ and not exc.__suppress_context__:
            ctx = exc.__context__
            _print_tb("An error occurred", type(ctx), ctx, ctx.__traceback__)
            if not _has_rich:
                print(
                    "\n────While handling the previous exception, a new exception has occurred────\n"
                )
            else:
                print(
                    "\n────[red]While handling the previous exception, a new exception has occurred[/red]────\n"
                )
            _print_tb("Another error occurred", exc_type, exc, tb)
        else:
            _print_tb("An error occurred", exc_type, exc, tb)
        if config.debugger:
            import pdb  # pdb for python debugger bulls--(this comment got cut due to some reason)

            if not _has_rich:
                print("\nDebugger active. Type 'q' to quit.")
            else:
                print("\n[cyan]Debugger active. Type 'q' to quit.[/cyan]")
            pdb.post_mortem(tb)
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            if not _has_rich:
                print("ERROR: User interrupt")
            else:
                print("[red][bold]ERROR[/bold]: User interrupt[/red]")
            return
        else:
            if not _has_rich:
                print("ERROR: Failed to print traceback")
                print(f"Exc_obj: {repr(e)}\n")
                print("Original exception was:")
            else:
                print("[red][bold]ERROR[/bold]: Failed to print traceback")
                print(f"[red bold]Exc_obj[/red bold]: {repr(e)}\n")
                print("[red]Original exception was:[red]")
            sys.__excepthook__(exc_type, exc, tb)


def _threadhook(args: threading.ExceptHookArgs):
    """
    _threadhook() is the same as _customhook() except it is for threading tracebacks
    Args:
        args (ExceptHookArgs): The argument for the exception
    Returns:
        None
    ## Used by:
        initialize()
    ## Notes:
        It is an internal function, so don't call it
    """
    if not _has_rich:
        print(f"Exception in {args.thread.name}")
    else:
        print(f"[cyan]Exception in {args.thread.name}[/cyan]")
    _customhook(args.exc_type, args.exc_value, args.exc_traceback)


def _unraisablehook(unraisable) -> None:
    """_unraisablehook() is the same as _customhook() except it is for unraisable tracebacks
    Args:
        unraisable (UnraisableHookArgs): The unraisable object thingie
    Returns:
        None
    ## Used by:
        sys.unraisablehook
    ## Notes:
        - It is an internal function, so don't use it!
    """
    # this thing is so short bruh
    if not _has_rich:
        print(f"Exception ignored in: {unraisable.object}")
    else:
        print(f"[yellow]Exception ignored in: {unraisable.object}[/yellow]")
    _customhook(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback)


def initialize(
    *,
    show_locals=True,
    log_exceptions=False,
    debugger=False,
    mode="verbose",
    theme="monokai",
    background_color="default",
    use_config=False,
) -> None:
    """
    initialize() sets sys.excepthook, threading.excepthook and sys.unraisablehook to the custom hook
    Returns:
        None
    Example:
        ```
        >>> from better_trace import initialize
        >>> initialize()
        >>> sayori
        -----------An error occurred-----------
        File "<python-input-2>", line 1, in <module>
           sayori
        NameError: name 'sayori' is not defined
        ```
    ## Used by:
        sys.excepthook, threading.excepthook, and sys.unraisablehook
    ## Notes:
        - Use it like this - initialize() and not like this - sys.excepthook = initialize or threading.excepthook = initialize
        - This function is the opposite to revert, if you want to revert back to the original traceback, call revert
    """
    # if you understood the reference in the docstring example, you're a weebster ;)
    if use_config:
        try:
            with open("better_trace_config.toml", "rb") as f:
                config_file = tomllib.load(f)
                cfg = config_file.get("better_trace", {})
                mode = cfg.get("mode", mode)
                show_locals = cfg.get("show_locals", show_locals)
                theme = cfg.get("theme", theme)
                background_color = cfg.get("background_color", background_color)
                log_exceptions = cfg.get("log_exceptions", log_exceptions)
                debugger = cfg.get("debugger", debugger)
        except OSError:
            pass

    config.show_locals = show_locals
    config.log_exceptions = log_exceptions
    config.mode = _initialize_mode(mode)
    config.debugger = debugger
    config.theme = theme
    config.background_color = background_color

    sys.excepthook = _customhook
    threading.excepthook = _threadhook
    sys.unraisablehook = _unraisablehook


def demo() -> None:
    """
    demo() is a function that intentionally raises a ZeroDivisionError to show the formatting of the traceback
    Returns:
        None
    Example:
        ```
        >>> from better_trace import demo
        >>> demo()
        -----------An error occurred-----------
        File ".../better_trace.py", line ..., in demo
            raise ZeroDivisionError("You tried to divide by 0!")
        ZeroDivisionError: You tried to divide by 0!
        ```
    ## Notes:
        - This function just showcases the traceback formatting
        - To actually get the traceback formatting, call initialize
    """
    try:
        raise ZeroDivisionError("You tried to divide by 0!")
    except ZeroDivisionError as e:
        _print_tb("An error occurred", type(e), e, e.__traceback__)


def revert() -> None:
    """
    revert() is used to revert the traceback, back to the original traceback
    Returns:
        None
    Example:
        ```
        >>> from better_trace import initialize, revert
        >>> initialize()
        >>> oyasumi # good night in japanese, also raises an error
        -----------An error occurred-----------
        File "<python-input-2>", line 1, in <module>
          oyasumi # good night in japanese, also raises an error
        NameError: name 'oyasumi' is not defined
        Did you mean: sum?
        >>> revert() # reverts the custom traceback format to the original traceback
        >>> oyasumi
        Traceback (most recent call last):
          File "<python-input-4>", line 1, in <module>
            oyasumi
        NameError: name 'oyasumi' is not defined
        ```
    ## Notes:
        - This function reverts sys.excepthook, threading.excepthook, and sys.unraisablehook to sys.__excepthook__, threading.__excepthook__, and sys.__unraisablehook__
        - This function is the opposite of initialize. If you want the custom formatting, call initialize
    """
    # oyasumi oyasumi close your eyes and you'll leave this dream
    sys.excepthook = sys.__excepthook__
    threading.excepthook = threading.__excepthook__
    sys.unraisablehook = sys.__unraisablehook__
