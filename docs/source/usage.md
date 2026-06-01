# Usage

## Basic setup
``` python
import better_trace

better_trace.initialize()
```
Once initialized, all uncaught exceptions will be displayed with enhanced formatting.

## Demo
Shows a sample exception purely for demonstration purposes
``` python
import better_trace

better_trace.demo()
```

## Example: Simple exception
``` python
import better_trace

better_trace.initialize()

def divide(a: int, b: int) -> float:
    return a / b

print(divide(1, 0))
```
Instead of the normal python traceback, you will see:
- A **rich** and **colorful** traceback with **syntax highlighting**
- Exact **line** of failure with **context** surrounding it
- Local variables (if enabled)

## Example: Debugging a real bug
``` python
import better_trace

better_trace.initialize()

def import_module(module: str):
    return __import__(module)

import_module("maths")
```
In this scenario, it would highlight the line, show the surrounding context, and also suggest the most similar module name

## Disable formatter
To disable formatter, do
``` python
better_trace.revert()
```