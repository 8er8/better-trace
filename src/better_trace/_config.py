"""
This module is created to resolve circular imports
"""

from dataclasses import dataclass


@dataclass(slots=True, repr=False, eq=False)
class _Config:
    show_locals: bool = True
    log_exceptions: bool = False
    mode: str = "verbose"
    debugger: bool = False
    theme: str = "monokai"
    background_color: str = "default"


config = _Config()
