from types import TracebackType
from typing import Any
import inspect
import pathlib
import os
import linecache
import io
import keyword
import tokenize
import reprlib
import traceback

_has_rich: bool = True

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

    console = Console()
except ModuleNotFoundError:
    _has_rich = False

from ._config import config
from ._did_you_mean import (
    suggest_name_error,
    suggest_attribute_error,
    suggest_module_not_found_error,
    suggest_import_error,
)


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
    if not _has_rich:
        for i in range(start, end + 1):
            line = linecache.getline(filename, i).rstrip("\n")
            prefix = "❱ " if i == lineno else "  "
            print(f"{prefix}{i:4} │ {line}")
        return

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
    else:  # for repl file names (like <stdin>)
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


def _give_filtered_locals(tb: TracebackType) -> list[Any]:
    filtered = []
    for k, v in tb.tb_frame.f_locals.items():
        if k.lower() in [
            "password",
            "token",
            "key",
            "api_key",
            "api_token",
            "api_password",
            "secret",
            "secrets",
            "passwords",
            "tokens",
            "keys",
            "api_passwords",
            "api_tokens",
            "api_keys",
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
    return filtered


def _print_notes(exc: BaseException) -> None:
    notes: list[str] | None = getattr(exc, "__notes__", None)
    if not notes:
        return
    if not _has_rich:
        print("\nNotes:")
    else:
        print("[cyan bold]\nNotes:[/cyan bold]")

    prefix = "[cyan]-[/cyan] " if _has_rich else "- "
    for note in notes:
        print(f"  {prefix}{note}")


def print_exception_group(
    group: ExceptionGroup,
    tb: TracebackType,
    prefix="",
    index_prefix="",
    is_root=True,
):
    """
    _print_exception_group is used to print the message if the exception type was an ExceptionGroup.
    """
    from .better_trace import _print_tb

    if is_root:
        _print_tb("Exception group error", type(group), group, tb)

    children = group.exceptions

    for i, exc in enumerate(children, start=1):
        last = i == len(children)

        branch = "╰── " if last else "├── "
        child_prefix = prefix + ("    " if last else "│   ")

        number = f"{index_prefix}.{i}" if index_prefix else str(i)

        if isinstance(exc, ExceptionGroup):
            if not _has_rich:
                print(prefix + branch + f"{number}. " + f"ExceptionGroup: {exc}")
            else:
                print(
                    prefix
                    + branch
                    + f"[cyan bold]{number}.[/cyan bold] "
                    + f"[red][bold]ExceptionGroup[/bold]: {exc}[/red]"
                )

            print_exception_group(
                exc,
                tb,
                child_prefix,
                number,
                False,
            )

        else:
            if not _has_rich:
                print(prefix + branch + f"{number}. " + f"{type(exc).__name__}]: {exc}")
            else:
                print(
                    prefix
                    + branch
                    + f"[cyan bold]{number}.[/cyan bold] "
                    + f"[red][bold]{type(exc).__name__}[/bold]: {exc}[/red]"
                )


def render_syntax_error(exc: SyntaxError, heading: bool = True) -> None:
    line = exc.text.rstrip("\n").expandtabs(4)

    start = (exc.offset or 1) - 1
    end = (exc.end_offset or exc.offset or 1) - 1

    if not _has_rich:
        if heading:
            print(f"Parsing Error".center(50, "─"))
        print(f'File "{exc.filename}", line {exc.lineno}')
        print(f"  {line}")
        print(f'  {" " * start + "^" * max(1, end - start)}')
        print(f"{type(exc).__name__}: {exc.msg}")
    else:
        if heading:
            print(f"[red]Parsing Error[/red]".center(50, "─"))
        print(f'File "{exc.filename}", line {exc.lineno}')
        print(f"[red]  {line}[/red]")
        print(f'[red]  {" " * start + "^" * max(1, end - start)}[/red]')
        print(f"[red][bold]{type(exc).__name__}[/bold]: {exc.msg}[/red]")


def print_debug(
    title: str,
    frames: traceback.StackSummary,
    exc_type: type[BaseException],
    exc: BaseException,
    tb: TracebackType,
) -> None:

    if not _has_rich:
        print(f"{title + ' (Debug mode)'}".center(50, "─") if title is not None else "")
    else:
        print(
            f"[red]{title + ' (Debug mode)'}[/red]".center(50, "─")
            if title is not None
            else ""
        )
    prev_key = None
    count = 0
    prev_frame = None
    last_tb = tb
    while last_tb.tb_next is not None:
        last_tb = last_tb.tb_next

    for frame in frames:
        key = (frame.filename, frame.name)
        if key == prev_key:
            count += 1
        else:
            if prev_frame:
                if not _has_rich:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno}, in {prev_frame.name}'
                    )
                    if not prev_frame.line:
                        print("  <line unavailable>  ")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno, 3)
                    if count > 3:
                        print(f"(Previous line repeated {count-1} times)")
                else:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
                    )
                    if not prev_frame.line:
                        print("[red bold]  <line unavailable> [/red bold]")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno, 3)
                    if count > 3:
                        print(
                            f"[cyan](Previous line repeated {count-1} more times)[/cyan]"
                        )
                filtered = _give_filtered_locals(tb)
                tokens = tokenize.generate_tokens(io.StringIO(frame.line).readline)

                uvariables = {
                    token.string
                    for token in tokens
                    if token.type == tokenize.NAME
                    and not keyword.iskeyword(token.string)
                }

                if config.show_locals and filtered:
                    if not _has_rich:
                        print("Local variables:")
                    else:
                        print("[yellow]Local variables:[/yellow]")
                for k, v, t in filtered:
                    if not _has_rich:
                        if k in uvariables:
                            print(f" {k} ({t}) = {v} (used)")
                        else:
                            print(f" {k} ({t}) = {v}")
                    else:
                        if k in uvariables:
                            print(f" {k} ({t}) = {v} [green](used)[/green]")
                        else:
                            print(f" {k} ({t}) = {v}")

                print("─" * 40)
                tb = tb.tb_next
            prev_frame = frame
            prev_key = key
            count = 1
    if prev_frame:
        if not _has_rich:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in {prev_frame.name}'
            )
            if not prev_frame.line:
                print("  <line unavailable>  ")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno, 3)
            if count > 3:
                print(f"(Previous line repeated {count-1} times)")
        else:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
            )
            if not prev_frame.line:
                print("[red bold]  <line unavailable> [/red bold]")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno, 3)
            if count > 3:
                print(f"[cyan](Previous line repeated {count-1} more times)[/cyan]")
            filtered = _give_filtered_locals(tb)
            if config.show_locals and filtered:
                if not _has_rich:
                    print("Local variables:")
                else:
                    print("[yellow]Local variables:[/yellow]")
                for k, v, t in filtered:
                    if not _has_rich:
                        if k in uvariables:
                            print(f" {k} ({t}) = {v} (used)")
                        else:
                            print(f" {k} ({t}) = {v}")
                    else:
                        if k in uvariables:
                            print(f" {k} ({t}) = {v} [green](used)[/green]")
                        else:
                            print(f" {k} ({t}) = {v}")
        print("─" * 40)
        tb = tb.tb_next
    if _has_rich:
        print("[yellow]Call stack:[/yellow]")
    else:
        print("Call stack:")
    prev_key = None
    count = 0
    prev_frame = None
    indentation = 1

    for frame in frames:
        key = (frame.filename, frame.name)
        if key == prev_key:
            count += 1
        else:
            if prev_frame:
                if _has_rich:
                    if count > 3:
                        print(
                            f"{' ' * indentation} ╰── [cyan][bold]{prev_frame.name}[/bold][/cyan]"
                            + f" [bold cyan](x{count-1})[/bold cyan]"
                        )
                    else:
                        for _ in range(count):
                            print(
                                f"{' ' * indentation} ╰── [cyan][bold]{prev_frame.name}[/bold][/cyan]"
                            )
                            indentation += 2

                    indentation += 2
                else:
                    if count > 3:
                        print(
                            f"{' ' * indentation}╰── {prev_frame.name}" + f" {count-1}"
                        )

                    else:
                        for _ in range(count):
                            print(f"{' ' * indentation}╰── {prev_frame.name}")
                            indentation += 2
            prev_frame = frame
            prev_key = key
            count = 1
    if prev_frame:
        if _has_rich:
            if count > 3:
                print(
                    f"{' ' * indentation} ╰── [cyan][bold]{prev_frame.name}[/bold][/cyan]"
                    + f" [bold cyan](x{count-1})[/bold cyan]"
                )
            else:
                for _ in range(count):
                    print(
                        f"{' ' * indentation} ╰── [cyan][bold]{prev_frame.name}[/bold][/cyan]"
                    )
                    indentation += 2
        else:
            if count > 3:
                print(f"{' ' * indentation}╰── {prev_frame.name}" + f" (x{count-1})")
            else:
                for _ in range(count):
                    print(
                        f"{' ' * indentation} ╰── [cyan][bold]{prev_frame.name}[/bold][/cyan]"
                    )
                    indentation += 2
    print("─" * 40)

    name = exc_type.__name__ or "UnknownError"
    msg = str(exc) or "<no message provided>"
    issyntaxerror = isinstance(exc, SyntaxError)

    if not issyntaxerror:
        has_filename = False
        has_len = False
    elif (exc.filename is None) or (exc.lineno is None):
        has_filename = False
        has_len = False
    else:
        has_filename = True
        has_len = True

    if not (issyntaxerror and has_filename and has_len):
        if not _has_rich:
            print(f"{name}: {msg}")
        else:
            print(f"[red][bold]{name}[/bold][/red]: [red]{msg}[/red]")

    if issyntaxerror and has_filename and has_len:
        render_syntax_error(exc, heading=False)

    if isinstance(exc, NameError):
        suggest_name_error(exc, last_tb)

    if isinstance(exc, AttributeError):
        suggest_attribute_error(exc)

    if isinstance(exc, ModuleNotFoundError):
        suggest_module_not_found_error(exc)

    if isinstance(exc, ImportError):
        suggest_import_error(exc)

    _print_notes(exc)


def print_verbose(
    title: str,
    frames: traceback.StackSummary,
    exc_type: type[BaseException],
    exc: BaseException,
    tb: TracebackType,
) -> None:
    if not _has_rich:
        print(f"{title}".center(50, "─") if title is not None else "")
    else:
        print(f"[red]{title}[/red]".center(50, "─") if title is not None else "")
    prev_key = None
    count = 0
    prev_frame = None
    for frame in frames:
        key = (frame.filename, frame.name)
        if key == prev_key:
            count += 1
        else:
            if prev_frame:
                if not _has_rich:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno}, in {prev_frame.name}'
                    )
                    if not prev_frame.line:
                        print("  <line unavailable>  ")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno)
                    if count > 3:
                        print(f"(Previous line repeated {count-1} times)")
                else:
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
                print("─" * 40)
            prev_frame = frame
            prev_key = key
            count = 1
    if prev_frame:
        if not _has_rich:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in {prev_frame.name}'
            )
            if not prev_frame.line:
                print("  <line unavailable>  ")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno)
            if count > 3:
                print(f"(Previous line repeated {count-1} times)")
        else:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
            )
            if not prev_frame.line:
                print("[red bold]  <line unavailable> [/red bold]")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno)
            if count > 3:
                print(f"[cyan](Previous line repeated {count-1} more times)[/cyan]")
        print("─" * 40)

    while tb.tb_next:
        tb = tb.tb_next

    filtered = _give_filtered_locals(tb)
    if config.show_locals and filtered:
        if not _has_rich:
            print("Local variables (last frame):")
        else:
            print("[yellow]Local variables (last frame):[/yellow]")
        for k, v, t in filtered:
            print(f" {k} ({t}) = {v}")

    name = exc_type.__name__ or "UnknownError"
    msg = str(exc) or "<no message provided>"
    issyntaxerror = isinstance(exc, SyntaxError)
    if not issyntaxerror:
        has_filename = False
        has_len = False
    elif (exc.filename is None) or (exc.lineno is None):
        has_filename = False
        has_len = False
    else:
        has_filename = True
        has_len = True

    if not (issyntaxerror and has_filename and has_len):
        if not _has_rich:
            print(f"{name}: {msg}")
        else:
            print(f"[red][bold]{name}[/bold][/red]: [red]{msg}[/red]")

    if issyntaxerror and has_filename and has_len:
        render_syntax_error(exc, heading=False)

    if isinstance(exc, NameError):
        suggest_name_error(exc, tb)

    if isinstance(exc, AttributeError):
        suggest_attribute_error(exc)

    if isinstance(exc, ModuleNotFoundError):
        suggest_module_not_found_error(exc)

    if isinstance(exc, ImportError):
        suggest_import_error(exc)

    _print_notes(exc)


def print_context(
    frames: traceback.StackSummary,
    exc_type: type[BaseException],
    exc: BaseException,
    tb: TracebackType,
) -> None:
    frames = frames[-50:]
    prev_key = None
    count = 0
    prev_frame = None
    if not _has_rich:
        print("── Traceback (context mode) ──")
    else:
        print("── [red]Traceback (context mode)[/red] ──")
    for frame in frames:
        key = (frame.filename, frame.name)
        if key == prev_key:
            count += 1
        else:
            if prev_frame:
                if not _has_rich:
                    print(
                        f'File "{prev_frame.filename}", line {prev_frame.lineno} in {prev_frame.name}'
                    )
                    if not prev_frame.line:
                        print(f"  <line unavailable>  ")
                    else:
                        _show_context(prev_frame.filename, prev_frame.lineno, 1)
                    if count > 3:
                        print(f"(Previous line repeated {count-1} more times)")
                else:
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
                print("─" * 40)
            prev_frame = frame
            prev_key = key
            count = 1
    if prev_frame:
        if not _has_rich:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno} in {prev_frame.name}'
            )
            if not prev_frame.line:
                print(f"  <line unavailable>  ")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno, 1)
            if count > 3:
                print(f"(Previous line repeated {count-1} more times)")
        else:
            print(
                f'File "{prev_frame.filename}", line {prev_frame.lineno}, in [yellow][bold]{prev_frame.name}[/bold][/yellow]'
            )
            if not prev_frame.line:
                print("[red bold]  <line unavailable>  [/red bold]")
            else:
                _show_context(prev_frame.filename, prev_frame.lineno, 1)
            if count > 3:
                print(f"[cyan](Previous line repeated {count-1} more times)[/cyan]")
        print("─" * 40)
    while tb.tb_next:
        tb = tb.tb_next

    name = exc_type.__name__ or "UnknownError"
    msg = str(exc) or "<no message provided>"
    issyntaxerror = isinstance(exc, SyntaxError)
    if not issyntaxerror:
        has_filename = False
        has_len = False
    elif (exc.filename is None) or (exc.lineno is None):
        has_filename = False
        has_len = False
    else:
        has_filename = True
        has_len = True

    if not (issyntaxerror and has_filename and has_len):
        if not _has_rich:
            print(f"{name}: {msg}")
        else:
            print(f"[red][bold]{name}[/bold][/red]: [red]{msg}[/red]")

    if issyntaxerror and has_filename and has_len:
        render_syntax_error(exc, heading=False)

    if isinstance(exc, NameError):
        suggest_name_error(exc, tb)

    if isinstance(exc, AttributeError):
        suggest_attribute_error(exc)

    if isinstance(exc, ModuleNotFoundError):
        suggest_module_not_found_error(exc)

    if isinstance(exc, ImportError):
        suggest_import_error(exc)

    _print_notes(exc)


def print_compact(
    frames: traceback.StackSummary,
    exc_type: type[BaseException],
    exc: BaseException,
    tb: TracebackType,
) -> None:
    frames = frames[-3:]
    if not _has_rich:
        print("── Traceback (compact mode) ──")
    else:
        print("[red]── Traceback (compact mode) ──[/red]")
    for i, frame in enumerate(frames):
        is_last = i == len(frames) - 1

        if not _has_rich:
            print(f"{pathlib.Path(frame.filename).name}:{frame.lineno} -> {frame.name}")
        else:
            print(
                f"[yellow]{pathlib.Path(frame.filename).name}[/yellow]:{frame.lineno} -> [cyan]{frame.name}[/cyan]"
            )
        prefix = "❱ " if is_last else "  "
        if frame.line:
            if not _has_rich:
                print(f"{prefix}{frame.line}")
            else:
                print(prefix, end="")
                console.print(
                    Syntax(
                        frame.line,
                        lexer="python",
                        theme=config.theme,
                        background_color=config.background_color,
                    )
                )
    while tb.tb_next:
        tb = tb.tb_next

    msg = str(exc) or "<no error message>"
    if not _has_rich:
        print(f"{exc_type.__name__}: {msg}")
    else:
        print(f"[red][bold]{exc_type.__name__}[/bold]: {msg}[/red]")

    if issubclass(exc_type, NameError):
        suggest_name_error(exc, tb)

    if isinstance(exc, AttributeError):
        suggest_attribute_error(exc)

    if isinstance(exc, ModuleNotFoundError):
        suggest_module_not_found_error(exc)

    if isinstance(exc, ImportError):
        suggest_import_error(exc)


def print_minimal(
    frames: traceback.StackSummary,
    exc_type: type[BaseException],
    exc: BaseException,
    tb: TracebackType,
) -> None:
    _hidden_count = len(traceback.extract_tb(tb)) - 1

    print("[red]── Exception ──[/red]") if _has_rich else print("── Exception ──")
    frames: traceback.StackSummary = frames[-1:]
    for frame in frames:
        if not _has_rich:
            print(f"{pathlib.Path(frame.filename).name}:{frame.lineno} -> {frame.name}")
            print(f"> {frame.line}")
            print(
                f"{exc_type.__name__ or 'UnknownError'}: {str(exc) or '<no message provided'}"
            )
        else:
            print(
                f"[yellow]{pathlib.Path(frame.filename).name}[/yellow]:{frame.lineno} -> [cyan]{frame.name}[/cyan]"
            )
            print(f"[red][bold]>[/bold]  {frame.line}[/red]")
            print(
                f"[red][bold]{exc_type.__name__ or 'UnknownError'}[/bold]: {str(exc) or '<no message provided>'}[/red]"
            )
    if _hidden_count > 0:
        print(f"[cyan]({_hidden_count} frame(s) hidden due to minimal mode)[/cyan]")
