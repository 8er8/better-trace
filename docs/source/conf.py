project = "better-trace"
author = "Adamya Mondal"
release = "0.2.0"

extensions = [
    "myst_parser",
    "autoapi.extension"
]
myst_enable_extensions = [
    "colon_fence",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "furo"

autoapi_type = "python"
autoapi_dirs = ["../../src/"]
root_doc = "index"