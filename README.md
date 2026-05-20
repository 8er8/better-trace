# Better-trace
[![License: MIT](https://img.shields.io/badge/License-MIT-Yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/better-trace.svg)](https://pypi.org/project/better-trace)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)


A Python tool to make tracebacks colorful, context-rich, developer friendly, and turns  
python crashes to something you can easily read
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
### Cloning github repo
You can install better-trace by cloning the git directory by  
`git clone https://github.com/8er8/better-trace.git`  
Now you can choose one of the following options to install better-trace
#### Option 1: Install normally (recommended) 
`cd better-trace`  
`python3 -m pip install .`  
#### Option 2: Install in editable mode (best for development)
`cd better-trace`  
`python3 -m pip install -e .`

### Install using PyPI
Type this command to your shell--  
`python3 -m pip install better-trace`
#### Notes
- Requires Python >= 3.11
- python3 may not work on windows, so use python or py
## Quick example
``` python 
from better_trace import initialize

initialize()

# a crash
1 / 0
```
## Configuration
``` python 
initialize(
    show_locals=True,
    log_exceptions=False,
    debugger=False,
    mode="verbose",
    theme="monokai",
    background_color="default",
)
```
| Option | Description |
| ----------|-------------- |
| show_locals  |   Shows locals at crash site (default=True)       | 
| log_exceptions | Logs exceptions to crash.log (default=False) |
| debugger | Enables pdb after exception (default=False)|
| mode | Output style (verbose, context, compact, minimal) (default="verbose") |
| theme | The syntax highlighting theme (default="monokai") |
| background_color | The background color (default="default")|
## Mode preview
### Verbose
full traceback + locals + context  
Shows everything  
![Verbose mode output](https://raw.githubusercontent.com/8er8/better-trace/main/assets/better_trace_verbose.png)
### Context
Balanced output with surrounding lines  
![Context mode output](https://raw.githubusercontent.com/8er8/better-trace/main/assets/better_trace_context.png)
### Compact
Short and readable  
![Compact mode output](https://raw.githubusercontent.com/8er8/better-trace/main/assets/better_trace_compact.png)
### Minimal
Just the last frame and the error line  
![Minimal mode output](https://raw.githubusercontent.com/8er8/better-trace/main/assets/better_trace_minimal.png)
## Better-trace demo
``` python
from better_trace import demo

demo()
```
## Reverting back
``` python
from better_trace import revert

revert()
```
## Before and After
### Before
``` text
Traceback (most recent call last):
  File "C:\python\Adamya\a.py", line 10, in <module>
    main()
  File "C:\python\Adamya\a.py", line 7, in main
    print(my_var)
NameError: name 'my_va' is not defined
```
### After
![Better-trace output](https://raw.githubusercontent.com/8er8/better-trace/main/assets/better_trace_verbose.png)
## Notes
- Requires `rich`
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
### License
This project is licensed under the MIT license