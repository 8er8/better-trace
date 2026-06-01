# API

## Public functions

### `initialize()`
Enables custom traceback formatting

``` python
import better_trace

better_trace.initialize()
```

### `revert()`
Disables custom traceback formatting
``` python
import better_trace

better_trace.revert()
```

### `demo()`
Displays a traceback for demonstration purposes
``` python
import better_trace

better_trace.demo()
```
## Configuration for `initialize()`
``` python 
better_trace.initialize(
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

## Behavior
This tool overrides the global Python exception handler (`sys.excepthook`) for the current process.