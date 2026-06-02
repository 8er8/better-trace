from importlib.metadata import version
from .better_trace import initialize, demo, revert

__all__ = ['initialize', 'demo', 'revert']
__version__ = version("better-trace")