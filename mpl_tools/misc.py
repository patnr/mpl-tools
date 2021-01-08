import json
import os
import platform

import matplotlib as mpl
from matplotlib import pyplot as plt

__all__ = [
    "thousands", "freshfig",
    "get_fig_geo", "set_fig_geo", "fig_placement_save", "fig_placement_load",
    "get_legend_bbox",
    "is_notebook_or_qt", "axprops", "fig_colorbar"]

thousands = mpl.ticker.StrMethodFormatter('{x:,.7g}')

_FIG_GEOMETRIES_PATH = "./.fig_geometries"

try:
    __IPYTHON__
    from IPython import get_ipython
    is_notebook_or_qt = 'zmq' in str(type(get_ipython())).lower()
except (NameError, ImportError):
    is_notebook_or_qt = False


def freshfig(num=None, figsize=None, *args, **kwargs):
    """Create/clear figure.

    Similar to:

    >>> fig, ax = suplots(*args,**kwargs)

    With the modification that:

    - If the figure does not exist: create it.
      This allows for figure sizing -- even with mpl backend MacOS.
    - Otherwise: clear figure.
      Avoids closing/opening so as to keep pos and size.
    """
    # exists = plt.fignum_exists(num)

    fig = plt.figure(num=num, figsize=figsize)
    fig.clear()

    _, ax = plt.subplots(num=fig.number, *args, **kwargs)
    return fig, ax


def _get_fmw(fignum):
    """If this fails, there's probs no way to make placement work."""
    return plt.figure(fignum).canvas.manager.window


def get_fig_geo(fignum):
    fmw = _get_fmw(fignum)
    try:
        # For Qt4Agg/Qt5Agg
        return dict(
            w=fmw.width(),
            h=fmw.height(),
            x=fmw.x(),
            y=fmw.y(),
        )
    except Exception:
        # For TkAgg
        return fmw.geometry()


def set_fig_geo(fignum, geo):
    plt.figure(int(fignum))
    fmw = _get_fmw(int(fignum))
    try:
        # For Qt4Agg/Qt5Agg
        fmw.setGeometry(geo['x'], geo['y'], geo['w'], geo['h'])
    except Exception:
        # For TkAgg
        # geo = "{w:.0f}x{h:.0f}+{x:.0f}+{y:.0f}".format(**geo)
        fmw.geometry(newGeometry=geo)


def fig_placement_save(path=_FIG_GEOMETRIES_PATH, append_host=True):
    if append_host:
        path = ".".join([path, platform.node()])

    placements = {num: get_fig_geo(num) for num in plt.get_fignums()}

    with open(path, "w") as file:
        file.write(json.dumps(placements))


def fig_placement_load(path=_FIG_GEOMETRIES_PATH, append_host=True):
    if append_host:
        path = ".".join([path, platform.node()])

    if not os.path.exists(path):
        print("Warning: no saved figure placement found",
              f"under the name {path}.",
              "Create a new one using fig_placement_save().")
        return

    with open(path, "r") as file:
        placements = json.load(file)

    for num in placements:
        set_fig_geo(num, placements[num])


def get_legend_bbox(ax):
    """Get legend's bbox in pixel ("display") coords."""
    # Must pause/draw before bbox can be known
    def inner():
        plt.draw()
        leg = ax.get_legend()
        bbox = leg.get_window_extent()
        # bbox = leg.get_frame().get_bbox()
        return bbox
    return inner


# stackoverflow.com/a/11103301
def on_xlim_changed(ax):
    """
    Autoscale y-axis for subplots with sharex=True.

    Usage:
    for ax in fig.axes:
        ax.callbacks.connect('xlim_changed', on_xlim_changed)
    """
    import numpy as np
    xlim = ax.get_xlim()
    for a in ax.figure.axes:
        # shortcuts: last avoids n**2 behavior when each axis fires event
        if a is ax or len(a.lines) == 0 or getattr(a, 'xlim', None) == xlim:
            continue

        ylim = np.inf, -np.inf
        for ln in a.lines:
            x, y = ln.get_data()
            # faster, but assumes that x is sorted
            start, stop = np.searchsorted(x, xlim)
            yc = y[max(start - 1, 0):(stop + 1)]
            ylim = min(ylim[0], np.nanmin(yc)), max(ylim[1], np.nanmax(yc))

        # TODO: update limits from Patches, Texts, Collections, ...

        # x axis: emit=False avoids infinite loop
        a.set_xlim(xlim, emit=False)

        # y axis: set dataLim, make sure that autoscale in 'y' is on
        corners = (xlim[0], ylim[0]), (xlim[1], ylim[1])
        a.dataLim.update_from_data_xy(corners, ignore=True, updatex=False)
        a.autoscale(enable=True, axis='y')
        # cache xlim to mark 'a' as treated
        a.xlim = xlim


def axprops(dct):
    """Filters `dct` for properties associated with a plot axes.

    Example:
    >>> def myplotter(ax, x, y, **COMMON)
    >>>     ax.set(**axprops(COMMON))
    >>>     ax.plot(x, y, COMMON)
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
    """Add colorbar to the right on a figure."""
    fig.subplots_adjust(right=0.8)
    cax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = fig.colorbar(collections, cax, *args, **kwargs)
    plt.pause(0.1)
    return cbar
