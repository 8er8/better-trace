# Better-trace
[![License: MIT](https://img.shields.io/badge/License-MIT-Yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/better-trace.svg)](https://pypi.org/project/better-trace)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Docs](https://readthedocs.org/projects/better-trace/badge/?version=latest&style=flat)](https://better-trace.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/formatting-black-black.svg)](https://github.com/psf/black)


A Python tool to make tracebacks colorful, context-rich, developer-friendly, and visually easier to read

## Features
- A colorful traceback powered by rich
- Multiple modes
    - Verbose - Gives you all the information
    - Context - A balanced view of the traceback (Recommended)
    - Compact - Shows only the last 3 frames, good for quick debugging
    - Minimal - Shows only the last frame, containing the essentials to quickly debug, not for advanced debugging
- Smart suggestions for NameError
- Context view (shows the surrounding lines; only for verbose and context mode)
- ExceptionGroup support
- Thread + Unraisable hooks
- Optional logging to file
- Built-in post mortem debugger (pdb)

## Installation
Type this command to your shell:  
```bash
python3 -m pip install better-trace
```
> *Note*: Requires python >= 3.11; `python3` may not work on windows, so use `python` or `py`

## Installation for contributors
Clone the better-trace github repo and install better-trace (in editable mode)
```bash
git clone https://github.com/8er8/better-trace.git
cd better-trace
python3 -m pip install -e .
```

## Quick example
```python 
from better_trace import initialize

initialize()

# a crash
1 / 0
```
## Configuration
```python 
initialize(
    show_locals=True,
    log_exceptions=False,
    debugger=False,
    mode="verbose",
    theme="monokai",
    background_color="default",
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_locals` | `bool` | `True` | Shows locals at crash site |
| `log_exceptions` | `bool` | `False` | Logs exceptions to `crash.log` |
| `debugger` | `bool` | `False` | Enables `pdb` post mortem debugging |
| `mode` | `str` | `"verbose"` | Output style (`verbose`, `context`, `compact`, `minimal`) |
| `theme` | `str` | `"monokai"` | The syntax highlighting theme |
| `background_color` | `str` | `"default"` | The background color |

## Mode preview

### Verbose
full traceback + locals + context  
Shows everything  
![Verbose mode output](https://github.com/8er8/better-trace/raw/main/assets/better_trace_verbose.png)

### Context
Balanced output with surrounding lines  
![Context mode output](https://github.com/8er8/better-trace/raw/main/assets/better_trace_context.png)

### Compact
Short and readable  
![Compact mode output](https://github.com/8er8/better-trace/raw/main/assets/better_trace_compact.png)

### Minimal
Just the last frame and the error line  
![Minimal mode output](https://github.com/8er8/better-trace/raw/main/assets/better_trace_minimal.png)

## Better-trace demo
```python
from better_trace import demo

demo()
```

## Reverting back
```python
from better_trace import revert

revert()
```

## Before and After

### Before
```text
Traceback (most recent call last):
  File "C:\python\Adamya\a.py", line 10, in <module>
    main()
  File "C:\python\Adamya\a.py", line 7, in main
    print(my_va)
NameError: name 'my_va' is not defined
```

### After
![Better-trace output](https://github.com/8er8/better-trace/raw/main/assets/better_trace_verbose.png)

## Why better-trace?
Because the default python traceback is informative but is really ugly and sometimes hard to read.

But better-trace makes tracebacks easier to read by--
- Making tracebacks easier to read
- Giving more info
- Coloring and syntax higlighting powered by rich
- Four different modes
- And much more 

## Notes
- Optionally requires `rich`
- Works best in modern terminals
- Designed for developer experience (not beginner-oriented)

## Credits

### Main developer
**Adamya Mondal** - creator, designer, and maintainer of this project

### Built with
- Python Standard Library
- rich (Huge credits to developers of rich)

### Inspiration
Python's default traceback is really minimal    
So we fixed it to make it more
developer-friendly

### Contributions
- **Adamya Mondal** (for being the main dev)
- Open for contributors
> *Note*: Contributors who are willing to contribute better-trace should read the 'Installation for contributors' section

### License
This project is licensed under the MIT license