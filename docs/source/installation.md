# Installation

## Requirements
Python 3.11 or higher

## Install from PyPI
You can install better-trace via pip by
``` bash
python3 -m pip install better-trace
```
> *Note*:
`python3` may not be available for Windows, so use `python` or `py`.

## Verify the installation
Run this code to verify if the installation succeeded:
``` python
try:
    import better_trace
except ImportError:
    print("Installation failed!")
else:
    print("Installation succeeded!")
```
If it prints `"Installation succeeded!"`, then the package is installed correctly.

## Installation for developers / contributors
Clone the GitHub repository and install it
``` bash
git clone https://github.com/8er8/better-trace.git
cd better-trace
``` 
Install in editable mode:
``` bash
python3 -m pip install -e .
```
## Upgrading

### Installed via PyPI
``` bash
python3 -m pip install --upgrade better-trace
```
### Installed via git clone
``` bash
git pull
```