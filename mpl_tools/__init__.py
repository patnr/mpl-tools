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
    ip = str(type(get_ipython())).lower()
    is_notebook_or_qt = (
        ("zmq" in ip)  # local Jupyter, binder, Kaggle
        or ("colab" in ip)  # Google Colab
    )
except (NameError, ImportError):
    is_notebook_or_qt = False


def is_using_interactive_backend():
    """Check if `mpl` is (currently) using an interactive backend.

    This means that the figures may be shown on screen.
    But only if you've done `plt.ion` so that `mpl.is_interactive`,
    or after calling `plt.show`.

    Note on jupyter notebook backends:
    - `%matplotlib notebook` (`nbAgg`) is interactive.
    - `%matplotlib inline` is not, but still shows up in the notebook.
      It can also be updated; see `dapper/tools/viz:plot_pause()`.
      However, it does not allow for mouse interaction,
      as it is merely a static picture.
      It also uses different dpi than `nbAgg`, ref
      https://github.com/matplotlib/matplotlib/issues/4853
    - `%matplotlib widgets` is for Jupyterlab?
    """
    return mpl.get_backend() in mpl.rcsetup.interactive_bk
