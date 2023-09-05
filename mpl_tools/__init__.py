"""Documentation for mpl-tools.

## Dev guide
Also see `dev_guide`

## API reference
The rendered docstrings can be browsed
through the following links, which are also available in the left sidebar.
"""

import importlib.metadata as importlib_metadata
__version__ = importlib_metadata.version(__name__)


import matplotlib as mpl

# is_notebook_or_qt
# TODO: check how `tqdm.auto` does it
try:
    __IPYTHON__  # type: ignore
    from IPython import get_ipython  # type: ignore
    ip = str(type(get_ipython())).lower()
    is_notebook_or_qt = (
        ("zmq" in ip)  # local Jupyter, binder, Kaggle
        or ("colab" in ip)  # Google Colab
        # Note: it appears to be impossible to detect if we're in
        # jupyter-notebook or -lab https://discourse.jupyter.org/t/6935 .
        # Fortunately, for mpl, `%matplotlib widget/ipympl` works with both.
    )
except (NameError, ImportError):
    is_notebook_or_qt = False


def is_using_interactive_backend():
    """Check if `mpl` is (currently) using an interactive backend.

    - Examples of interactive: `Qt5Agg` and `MacOSX`
    - For jupyter notebooks, note that
        - `%matplotlib notebook` (`nbAgg`) is interactive.
        - `%matplotlib inline` is not. This means that
          it does not allow for mouse interaction, being a static picture,
          though it can still be updated, e.g. `dapper/tools/viz:plot_pause()`.
          It also uses different `dpi` than `nbAgg`,
          [ref](https://github.com/matplotlib/matplotlib/issues/4853)
        - `%matplotlib widgets/ipympl` is interactive,
          and works in Jupyter-lab, unlike (`nbAgg`).
          However, it is NOT listed among `interactive_bk`.
    """
    return mpl.get_backend() in mpl.rcsetup.interactive_bk


def is_inline():
    """Check if using IPython/Jupyter inline `mpl` backend.

    This is not the opposite of `is_using_interactive_backend`,
    because this is also `False` for backends: PNG, SVG, PDF, PS.
    """
    # return mpl.get_backend() == 'module://ipykernel.pylab.backend_inline'
    return "inline" in mpl.get_backend()
