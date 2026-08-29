from inspect import getsource

from druks import ui

# Every catalog page ends with the code that produced it, so a reader never has
# to guess which declaration made what they are looking at.
HEADING = "The declaration that made this page"


def declaration(page) -> ui.Markdown:
    """The page function's own source, as the page's last block."""
    body = getsource(page.function).rstrip()
    return ui.Markdown(f"### {HEADING}\n\n```python\n{body}\n```")
