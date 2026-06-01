project = "better-trace"
author = "Adamya Mondal"
release = "0.1.2"

extensions = [
    "myst_parser",
    "autoapi.extension"
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "furo"

autoapi_type = "python"
autoapi_dirs = ["../src/better_trace"]
root_doc = "index"