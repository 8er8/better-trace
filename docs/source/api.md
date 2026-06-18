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

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_locals` | `bool` | `True` | Shows locals at crash site |
| `log_exceptions` | `bool` | `False` | Logs exceptions to `crash.log` |
| `debugger` | `bool` | `False` | Enables `pdb` post mortem debugging |
| `mode` | `str` | `"verbose"` | Output style (`verbose`, `context`, `compact`, `minimal`) |
| `theme` | `str` | `"monokai"` | The syntax highlighting theme |
| `background_color` | `str` | `"default"` | The background color |

## Behavior
This tool overrides the global Python exception handler (`sys.excepthook`) for the current process.