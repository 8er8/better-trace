from types import TracebackType, ModuleType
import difflib
import builtins
import sys
import pkgutil
import importlib
import re

_has_rich: bool = True
try:
    from rich import print
except ModuleNotFoundError:
    _has_rich = False

all_modules = {module.name for module in pkgutil.iter_modules()}
all_modules.update(sys.builtin_module_names)

def suggest_name_error(exc: NameError, tb: TracebackType) -> None:
    """
    suggest_name_error is a function that takes two paramters, exc and tb.
    It is used to suggest 'Did you mean: ...? for NameErrors'
    Args:
        exc (NameError): The NameError object
        tb (TracebackType): The traceback object
    Returns:
        None
    ## Used by:
        - print_verbose
        - print_context
        - print_compact
        - print_minimal
    ## Notes:
        This is an internal function, so don't call it.
    """
    name = exc.name
    if not name:
        return

    candidates = set()

    candidates.update(tb.tb_frame.f_locals.keys())
    candidates.update(tb.tb_frame.f_globals.keys())
    candidates.update(dir(builtins))

    match = difflib.get_close_matches(name, candidates, n=1)
    if match:
        if not _has_rich:
            print(f"Did you mean: {match[0]}?")
        else:
            print(f"[cyan][bold]Did you mean[/bold]: {match[0]}?[/cyan]")

def suggest_attribute_error(exc: AttributeError) -> None:
    """
    suggest_attribute_error is a function that takes one paramter, exc.
    It is used to suggest 'Did you mean: ...? for AttributeErrors'
    Args:
        exc (AttributeError): The AttributeError object
    Returns:
        None
    ## Used by:
        - print_verbose
        - print_context
        - print_compact
        - print_minimal
    ## Notes:
        This is an internal function, so don't call it.
    """
    name = exc.name
    obj = exc.obj
    if not name:
        return
    
    match = difflib.get_close_matches(name, dir(obj))
    if not match:
        return
    if isinstance(obj, type):
        obj_name = obj.__name__
    elif isinstance(obj, ModuleType):
        obj_name = obj.__name__
    else:
        obj_name = type(obj).__name__
    
    if not _has_rich:
        print(f"Did you mean: {obj_name}.{match[0]}?")
    else: 
        print(f"[cyan][bold]Did you mean[/bold]: {obj_name}.{match[0]}?[/cyan]")

def suggest_module_not_found_error(exc: ModuleNotFoundError) -> None:
    if not exc.name:
        return
    target_name = exc.name.split('.')[0]
    match = difflib.get_close_matches(target_name, all_modules, n=1)
    
    if match:
        if not _has_rich:
            print(f"Did you mean: {match[0]}?")
        else:
            print(f"[cyan][bold]Did you mean[/bold]: {match[0]}?[/cyan]")

def suggest_import_error(exc: ImportError) -> None:
    if not exc.name:
        return
    
    try:
        module = importlib.import_module(exc.name)
    except Exception:
        return
    
    all_items = dir(module)
    match_msg = re.search(r"cannot import name '([^']+)'", str(exc))
    
    if not match_msg:
        return
    
    match = difflib.get_close_matches(match_msg.group(1), all_items, n=1)
    if match:
        if not _has_rich:
            print(f"Did you mean: from {exc.name} import {match[0]}?")
        else:   
            print(f"[cyan][bold]Did you mean[/bold]: from {exc.name} import {match[0]}?[/cyan]")