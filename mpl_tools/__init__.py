"""Documentation for mpl-tools.

## Dev guide
Also see `dev_guide`

## API reference
The rendered docstrings can be browsed
through the following links, which are also available in the left sidebar.
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
__version__ = importlib_metadata.version(__name__)


import matplotlib as mpl

try:
    __IPYTHON__  # type: ignore
    from IPython import get_ipython  # type: ignore
    is_notebook_or_qt = 'zmq' in str(type(get_ipython())).lower()
except (NameError, ImportError):
    is_notebook_or_qt = False


def is_using_interactive_backend():
    """Check fi mpl (currently) using an interactive backend.

    Not to be confused with plt.ion() state.
    """
    return mpl.get_backend() in mpl.rcsetup.interactive_bk
