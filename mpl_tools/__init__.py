"""Documentation.

Want tests to run on any level (pytest, tox, travis)

Screw cookiecutter and pyscaffold
coc-settings
Poetry/pyproject
Linting
 - Editor: useful
 - Precommit: useful
 - Travis: for PRs
 - As part of pytest - maybe for heavier (eg pylint) linting.
 - As part of tox - nah. This is one overlap too many

Installation and tasks with Makefile

Pytest
- Using mpl image comparison
Tox
pyenv
Travis-CI

    # AFAIK, the main reason to use tox on travis-ci (as well as locally)
    # is just to avoid repeating ourselves.


Deploy when git tag is pushed
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # noqa

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
__version__ = importlib_metadata.version(__name__)
