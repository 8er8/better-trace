from types import TracebackType
from dataclasses import dataclass
from warnings import warn
import sys
import traceback
import threading
import builtins
import inspect
import pathlib
import reprlib
import logging
import difflib
import os
import linecache

_safe_repr = reprlib.Repr()
_safe_repr.maxlevel = 2
_safe_repr.maxlist = 10
_safe_repr.maxdict = 10
_safe_repr.maxset = 10
_safe_repr.maxstring = 120
_safe_repr.maxother = 120

try:
    from rich import print
    from rich.syntax import Syntax
    from rich.console import Console
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Please install rich via python3 -m pip install -r requirements.txt"
    ) from None

__all__ = ["initialize", "demo", "revert"]
console = Console()
logging.basicConfig(
    filename="crash.log",
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.ERROR,
)
#  |----------------|
#  |  better-trace  |
#  |----------------|
# Traceback formatter for Python
# contributers - Adamya (me!)
# developers - Adamya (me!)
# license - MIT


@dataclass(slots=True, repr=False, eq=False)
class _Config:
    show_locals: bool = True
    log_exceptions: bool = False
    mode: str = "verbose"
    debugger: bool = False
    theme: str = "monokai"
    background_color: str = "default"


class InvalidModeWarning(Warning):
    pass


config = _Config()
_MODES = {"verbose", "context", "compact", "minimal"}



def _show_context(filename: str, lineno: int, context: int = 2):
    """
    _show_context() is a function that takes a filename, lineno, and context to show multiple  
    lines (contexts) instead of the usual one line per frame
    Args:
        filename (str): The filename of the file
        lineno (int): The line number of the file
        context (int): The amount of contexts to show (default = 2)
    Returns:
        None
    ## Used by:
        _print_tb
    ## Notes:
        This is an internal function, so don't call it.
    """
    start = max(1, lineno - context)
    end = lineno + context
    if os.path.exists(filename):    
        console.print(
            Syntax.from_path(
                filename,
                line_numbers=True,
                line_range=(start, end),
                highlight_lines={lineno},
                word_wrap=False,
                theme=config.theme,
                background_color=config.background_color,
            )
        )
    else: # for repl file names (like <stdin>)
        lines = []
        for i in range(start, end + 1):
            line = linecache.getline(filename, i)
            if line:
                prefix = "❱ " if i == lineno else "  "
                lines.append(f"{prefix}{line.rstrip()}")

        code = "\n".join(lines)

        console.print(
            Syntax(
                code,
                "python",
                theme=config.theme,
                background_color=config.background_color,
                line_numbers=True,
            )
        )


def _suggest_name_error(msg: str, tb: TracebackType):
    """
    _suggest_name_error is a function that takes two paramters, msg and tb.  
    It is used to suggest 'Did you mean: ...?'
    Args:
        msg (str): The exception message
        tb (TracebackType): The traceback object
    Returns:
        None
    ## Used by:
        _print_tb
    ## Notes:
        This is an internal function, so don't call it.
    """
    if "'" not in msg:
        return

    name = msg.split("'")[1]
    candidates = set()

    candidates.update(tb.tb_frame.f_locals.keys())
    candidates.update(tb.tb_frame.f_globals.keys())
    candidates.update(dir(builtins))

    match = difflib.get_close_matches(name, candidates, n=1)
    if match:
        print(f"[cyan][bold]Did you mean[/bold]: {match[0]}?[/cyan]")


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


def _print_exception_group(exc: ExceptionGroup, level: int = 0, index_prefix: str = ""):
    """
    _print_exception_group is used to print the message if the exception type was an ExceptionGroup.
    Args:
        exc (ExceptionGroup): The ExceptionGroup instance
        level (int): The level of index (default = 0)
        index_prefix (str): Basically the title (default = '')
    Returns:
        None
    ## Used by:
        _customhook
    ## Notes:
        This is an internal function, so don't call it.
    """
    indent = "  " * level

    title = f"{index_prefix}" if index_prefix else "Exception Group"
    print(f"{indent}[red]{title.center(50, '-')}[/red]")
    print(f"[cyan][bold]Message[/bold]: {str(exc) or '<no message available>'}[/cyan]")

    for i, sub in enumerate(exc.exceptions, 1):
        new_prefix = f"{index_prefix}{i}." if index_prefix else f"{i}."

        if isinstance(sub, ExceptionGroup):
            print(f"\n{indent}[cyan]Subgroup {new_prefix}[/cyan]")
            _print_exception_group(sub, level + 1, new_prefix)
        else:
            print(f"\n{indent}[cyan]Sub-exception {new_prefix}[/cyan]")
            _print_tb(
                f"Sub-exception {new_prefix}",
                type(sub),
                sub,
                sub.__traceback__,
                exceptgroup=True,
            )

def _print_verbose(
        title: str,
        frames: traceback.StackSummary,
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType
) -> None:
        print(f"[red]{title}[/red]".center(50, "-") if title is not None else "")
        prev_key = None
        count = 0
        prev_frame = None
        for frame in frames:
            key = (frame.filename, frame.name)
            if key == prev_key:
                count += 1
            else:
                if prev_frame:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
                    )
                    if not prev_frame.line:
                        print("[red bold]  <line unavailable> [/red bold]")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno)
                    if count > 3:
                        print(
                            f"[cyan](Previous line repeated {count-1} more times)[/cyan]"
                        )
                    print("-" * 40)
                prev_frame = frame
                prev_key = key
                count = 1
        if prev_frame:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
            )
            if not prev_frame.line:
                print("[red bold]  <line unavailable> [/red bold]")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno)
            if count > 3:
                print(f"[cyan](Previous line repeated {count-1} more times)[/cyan]")
            print("-" * 40)
        
        while tb.tb_next:
            tb = tb.tb_next

        filtered = []
        for k, v in tb.tb_frame.f_locals.items():
            if k in [
                "password",
                "token",
                "key",
                "api_key",
                "api_token",
                "api_password",
            ]:
                continue
            if k.startswith("__"):
                continue
            if inspect.ismodule(v):
                continue
            if inspect.isfunction(v):
                continue
            if isinstance(v, BaseException):
                continue
            try:
                val = _safe_repr.repr(v)
            except Exception:
                val = "<repr broken>"
            filtered.append((k, val, type(v).__name__))
        if config.show_locals and filtered:
            print("[yellow]\nLocal variables (last frame):[/yellow]")
            for k, v, t in filtered:
                print(f" {k} ({t}) = {v}")
        name = exc_type.__name__ if exc_type else "UnknownError"
        msg = str(exc) if exc else ""
        print(
            f"[red][bold]{name}[/bold][/red]: [red]{msg if msg else '<no message provided>'}[/red]"
        )
        if isinstance(exc, NameError):
            _suggest_name_error(msg, tb)

def _print_context(
        frames: traceback.StackSummary,
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType
) -> None:
        frames = frames[-50:]
        prev_key = None
        count = 0
        prev_frame = None
        print("-- [red]Traceback (context mode)[/red] --")
        for frame in frames:
            key = (frame.filename, frame.name)
            if key == prev_key:
                count += 1
            else:
                if prev_frame:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
                    )
                    if not prev_frame.line:
                        print("[red bold]  <line unavailable> [/red bold]")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno, 1)
                    if count > 3:
                        print(
                            f"[cyan](Previous line repeated {count-1} more times)[/cyan]"
                        )
                    print("-" * 40)
                prev_frame = frame
                prev_key = key
                count = 1
        if prev_frame:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
            )
            if not prev_frame.line:
                print("[red bold]  <line unavailable> [/red bold]")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno, 1)
            if count > 3:
                print(f"[cyan](Previous line repeated {count-1} more times)[/cyan]")
            print("-" * 40)
        while tb.tb_next:
            tb = tb.tb_next
        name = exc_type.__name__ if exc_type else "UnknownError"
        msg = str(exc) if exc else ""
        print(
            f"[red][bold]{name}[/bold][/red]: [red]{msg if msg else '<no message provided>'}[/red]"
        )
        if isinstance(exc, NameError):
            _suggest_name_error(msg, tb)

def _print_compact(
        frames: traceback.StackSummary,
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType
) -> None:
    frames = frames[-3:]
    print("[red] -- Traceback (compact mode) -- [/red]")
    for i, frame in enumerate(frames):
        is_last = i == len(frames) - 1
        print(
                f"[yellow]{pathlib.Path(frame.filename).name}[/yellow]:{frame.lineno} -> [cyan]{frame.name}[/cyan]"
            )
        prefix = "❱ " if is_last else "  "
        if frame.line:
            print(f"{prefix}{frame.line}")
    while tb.tb_next:
        tb = tb.tb_next
    msg = str(exc) or '<no error message>'
    print(f"[red][bold]{exc_type.__name__}[/bold]: {msg}[/red]")
    if issubclass(exc_type, NameError):
        _suggest_name_error(msg, tb)
        

def _print_minimal(
        frames: traceback.StackSummary,
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType,
) -> None:
        _hidden_count = len(traceback.extract_tb(tb)) - 1
        print("[red]-- Exception --[/red]")
        frames: traceback.StackSummary = frames[-1:]
        for frame in frames:
            print(
                f"[yellow]{pathlib.Path(frame.filename).name}[/yellow]:{frame.lineno} -> [cyan]{frame.name}[/cyan]"
            )
            print(f">  {frame.line}")
            print(
                f"[red][bold]{exc_type.__name__ if exc_type else 'UnknownError'}[/bold]: {str(exc) if str(exc) else '<no message provided>'}"
            )
        if _hidden_count > 0:
            print(f"[cyan]({_hidden_count} frame(s) hidden due to minimal mode)[/cyan]")

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
            print(
                f"[red]>[bold] {exc_type.__name__ if exc_type else 'UnknownError'}[/bold]: {str(exc) or '<no message provided>'}[/red]"
            )
            return
        builtins.print("ERROR: No traceback available")
        builtins.print("Printing original traceback...")
        sys.__excepthook__(exc_type, exc, tb)
        return
    if config.mode == "verbose":
        _print_verbose(title, frames, exc_type, exc, tb)
    
    elif config.mode == "context":
        _print_context(frames, exc_type, exc, tb)
    
    elif config.mode == "compact":
        _print_compact(frames, exc_type, exc, tb)
    
    elif config.mode == "minimal":
        _print_minimal(frames, exc_type, exc, tb)

    if config.log_exceptions:
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
            print("[yellow]Keyboard Interrupt[/yellow]".center(50, "-"))
            print("[yellow]The program was terminated by the user[/yellow]")
            print(
                "[cyan]Note: [/cyan]If you triggered it accidentally, note that Ctrl + C means KeyboardInterrupt"
            )
            return
        if exc_type and issubclass(exc_type, SyntaxError):
            if tb is None and exc is not None:
                print("[red]SyntaxError (detected in excepthook._customhook):[/red]")
                print(f'File "{exc.filename}", line {exc.lineno}')
                print(f"  [red]{exc.text.rstrip()}[/red]")
                print(f'[red]{" " * (exc.offset + 1) + "^^"}[/red]')
                print(f"[red][bold]{exc_type.__name__}[/bold]: {exc.msg}[/red]")
                return
        if isinstance(exc, ExceptionGroup):
            _print_exception_group(exc)
        if exc and exc.__cause__:
            cause = exc.__cause__
            _print_tb("An error occurred", type(cause), cause, cause.__traceback__)
            print(
                "\n----[red]The above exception was the cause of the other exception below[/red]----\n"
            )
            _print_tb("Another error occurred", exc_type, exc, tb)
        elif exc and exc.__context__ and not exc.__suppress_context__:
            ctx = exc.__context__
            _print_tb("An error occurred", type(ctx), ctx, ctx.__traceback__)
            print(
                "\n----[red]While handling the previous exception, a new exception has occurred[/red]----\n"
            )
            _print_tb("Another error occurred", exc_type, exc, tb)
        else:
            _print_tb("An error occurred", exc_type, exc, tb)
        if config.debugger:
            import pdb  # pdb for python debugger bulls--(this comment got cut due to some reason)

            print("\n[cyan]Debugger active. Type 'q' to quit.[/cyan]")
            pdb.post_mortem(tb)
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            print("[red][bold]ERROR[/bold]: User interrupt[/red]")
            return
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