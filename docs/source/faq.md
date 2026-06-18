# FAQ

## Why can't I see any colors?
Make sure your terminal supports ANSI colors, some IDE terminals and older terminals may not support them. Also, check if you have rich installed, since without rich, it would be rendered as plain text.

## Does it modify python internals?
No, it does not modify python internals, instead it modifies `sys.excepthook`, `threading.excepthook`, and `sys.unraisablehook`.

## I can't see the locals! Can you help me?
To enable locals, you must be in verbose mode and check if `show_locals=True` in initialize.

## Do I need rich for this?
You don't need rich for this project but as stated earlier, you would only see plain text instead of colorful text, so it is generally recommended to install rich (if not installed).

## Why doesn't better-trace affect exceptions inside a `try`-`except` block?
better-trace only formats uncaught errors, so if you catch them by using `try`-`except`, you would not see anything.

## Does better-trace work on IDEs?
Usually yes, but it depends on the IDE's terminal implementation.

## What Python versions are supported?
Python 3.11 and newer.

## How do I revert back to the original traceback?
You can simply revert back to the original traceback by calling `better_trace.revert()`.

## How do I install better-trace?
You can install better-trace by
```bash
python3 -m pip install better-trace
```
:::{note}
For detailed installation instructions, refer to the main installation guide.
:::

## Does better-trace support ExceptionGroups?
Yes, it does.
