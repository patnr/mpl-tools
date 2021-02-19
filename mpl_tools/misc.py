"""Misc mpl tools."""
import inspect
import warnings
from math import sqrt
from pathlib import Path

import matplotlib as mpl
from matplotlib import pyplot as plt

thousands = mpl.ticker.StrMethodFormatter('{x:,.7g}')  # type: ignore


def axprops(dct):
    """Filter `dct` for properties associated with a plot axes.

    Example
    -------
    >>> def myplotter(ax, x, y, **kwargs):
    ...     ax.set(**axprops(kwargs))  # Pop the kwargs belonging to ax
    ...     ax.plot(x, y, kwargs)      # Use rest as line props.
    """
    # List of included axis properties
    props = ["title", "facecolor", "aspect"]
    # Append xyz-specific props
    for ax in ["x", "y", "z"]:
        for p in ["label", "ticks", "scale", "lim"]:
            props.append(ax + p)

    # intersection(dct,props)
    props = {p: dct.pop(p) for p in props if p in dct}

    return props


def fig_colorbar(fig, collections, *args, **kwargs):
    """Add colorbar to the right on a figure.

    Example
    -------
    >>> fig, (ax1, ax2) = plt.subplots(nrows=2)
    >>> cs = ax1.contourf(np.arange(24).reshape((3,-1)), cmap=plt.cm.PuBu_r)
    >>> # fig.colorbar(cs)          # => colorbar to the right of ax2
    >>> cb = fig_colorbar(fig, cs)  # => colorbar on the right of figure.
    """
    fig.subplots_adjust(right=0.8)
    cax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = fig.colorbar(collections, cax, *args, **kwargs)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        plt.pause(.1)
    return cbar


def nRowCol(nTotal, figsize=None, axsize=None):
    """Compute `(nrows, ncols)` such that `nTotal ≈ nrows*ncols`.

    Takes into account the shapes of the figure and axes.
    Default figsize and axsize is taken from `mpl.rcParams`.

    Examples
    --------
    >>> nRowCol(4)
    {'nrows': 2, 'ncols': 2}
    >>> nRowCol(4, (4, 1), (1, 1))
    {'nrows': 1, 'ncols': 4}
    >>> nRowCol(4, (4, 1), (4, 1))
    {'nrows': 2, 'ncols': 2}
    >>> nRowCol(12, (4, 3), (1, 1))
    {'nrows': 3, 'ncols': 4}
    """
    # Defaults
    if figsize is None:
        figsize = mpl.rcParams["figure.figsize"]

    if axsize is None:
        rc = {k: mpl.rcParams["figure.subplot." + k]
              for k in ["bottom", "left", "right", "top"]}
        axsize = (rc["right"] - rc["left"],
                  rc["top"] - rc["bottom"])

    # Compute ratios
    w, h = figsize
    fig_ratio = w / h
    w, h = axsize
    ax_ratio = w / h
    ratio = fig_ratio / ax_ratio

    # Main logic
    nrows = round(sqrt(nTotal / ratio)) or 1
    ncols = nTotal // nrows
    # ncols rounds down, so we might have to increase it.
    if nrows * ncols < nTotal:
        ncols += 1

    return {"nrows": nrows, "ncols": ncols}


# TODO: re-include NicePrint from struct-tools?
class FigSaver():
    """Simplify exporting a figure, especially when it's part of a series."""

    def __init__(self, script=None, basename=None, n=-1, ext='.pdf'):
        """Init.

        Parameters
        ----------
        script: str
            Name of dir to put figs in. Defaults to stem of `__file__` of caller.

        basename: str
            Name of figure files.

        n: int
           Starting index for file names.

        Example
        -------
        >>> fs = FigSaver(n=1, ext=".eps") # doctest: +SKIP
        ... ax.plot(xdata, ydata) # Add line to plot
        ... fs.save()             # Save
        ... ax.plot(xdata, ydata) # Add another line
        ... fs.save()
        """
        # Defaults
        if script is None:  # Get __file__ of caller
            script = inspect.getfile(inspect.stack()[1][0])
        if basename is None:
            basename = 'figure'
        # Prep save dir
        sdir = Path(script).stem
        Path(sdir).mkdir(parents=True, exist_ok=True)
        # Set state
        self.fname = sdir + basename
        self.n     = n
        self.ext   = ext

    @property
    def fullname(self):
        """Get full name of figure to be saved."""
        f = self.fname            # Abbrev
        if self.n >= 0:           # If indexing:
            f += '_n%d' % self.n  # Add index
        f += self.ext             # Add extension
        return f

    def save(self):
        """Save current figure. Increments the index."""
        f = self.fullname           # Abbrev
        print("Saving fig to:", f)  # Print
        plt.savefig(f)              # Save
        if self.n >= 0:             # If indexing:
            self.n += 1                 # Increment
            plt.pause(0.1)              # For safety
