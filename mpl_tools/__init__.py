"""Documentation for mpl-tools

## Dev guide
Also see `dev_guide`

## API reference
The rendered docstrings can be browsed
through the following links, which are also available in the left sidebar.
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # noqa

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
__version__ = importlib_metadata.version(__name__)
