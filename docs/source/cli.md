# CLI

## Description
You can run better-trace by using your shell. It is good if you don't want to modify a python file.

## Basic usage
```bash
better-trace run app.py
```

## Syntax
```
better-trace <command (run | demo)> <flags> -- <flags to script>
```

## Options (for run)
| Option | Default | Description |
|--------|------|-------------|
| --show_locals | `True` | Shows locals at crash site |
| --log_exceptions | `False` | Logs exceptions to crash.log |
| --debugger | `False` | Enables pdb after exception |
| --mode (verbose\|context\|compact\|minimal) | `"verbose"` | Output style |
| --theme (theme) | `"monokai"` |  The syntax highlighting theme |
| background_color (bg_color) | `"default"` | The background color |

## Other commands
`demo`  
Usage:
```bash
better-trace demo
```