"""Documentation.

coc-settings
Poetry
Installation
- pip
- make
Pytest
- Using mpl image comparison
Tox
Travis-CI
Deploy when git tag is pushed
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # noqa

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
__version__ = importlib_metadata.version(__name__)
