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

    DEPRECATED. Use one of these methods instead:
    https://jdhao.github.io/2017/06/11/mpl_multiplot_one_colorbar/

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

    Takes into account the `figsize` and `axsize`, either of which
    may be given as a tuple, or a number (the ratio width/height).
    Defaults are taken from `mpl.rcParams`.

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
    try:
        w, h = figsize
        fig_ratio = w / h
    except TypeError:
        fig_ratio = figsize
    try:
        w, h = axsize
        ax_ratio = w / h
    except TypeError:
        ax_ratio = axsize
    ratio = fig_ratio / ax_ratio

    # Main logic
    nrows = round(sqrt(nTotal / ratio)) or 1
    ncols = nTotal // nrows
    # ncols rounds down, so we might have to increase it.
    if nrows * ncols < nTotal:
        ncols += 1

    return {"nrows": nrows, "ncols": ncols}


def zero_axes(ax, color=(.5, .5, .5), arrow_size=4,
              ticks=True, ticklabels=False, lw=None, tick_params=None):
    """Create axes with arrow spines which always go throw origin.

    Ref: <https://github.com/matplotlib/matplotlib/issues/17157>

    NB: `alpha` cannot be supported, because the spines consist of multiple elements,
    and where they overlap, the alphas overlay, creating non-homogenous effects.
    """
    if tick_params is None:
        tick_params = {
            "xtick.direction": "inout",
            "ytick.direction": "inout",
            "xtick.major.size": 6,
            "ytick.major.size": 6,
            "xtick.major.width": .5,
            "ytick.major.width": .5,
            "xtick.color": color,
            "ytick.color": color,
        }
    # Could also use ax.tick_params().
    with plt.rc_context(tick_params):
        plt.setp(ax.spines.values(), color=color, lw=lw)
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        if not ticks:
            ax.set_xticks([])
            ax.set_yticks([])
            # Alternative:
            # ax.xaxis.set_major_locator(plt.NullLocator())
        if not ticklabels:
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            # Alternative:
            # plt.setp( ax.get_xticklabels(), visible=False)

        # Arrow heads
        kws = dict(ls="", ms=arrow_size, color=color, clip_on=False)
        ax.plot((1), (0), marker=">", **kws, transform=ax.get_yaxis_transform())
        ax.plot((0), (1), marker="^", **kws, transform=ax.get_xaxis_transform())


def reverse_legend(ax, **kws):
    """Reverse order of legend items in `ax`."""
    leg = ax.get_legend_handles_labels()
    leg = list(map(list, zip(*leg)))[::-1]
    if leg:
        ax.legend(*zip(*leg), **kws)
