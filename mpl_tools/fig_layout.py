"""Tools for placing figures (not axes) on screen."""
import json
import platform
import warnings
from pathlib import Path

import matplotlib as mpl
from matplotlib import pyplot as plt

from mpl_tools import is_using_interactive_backend

_FIG_GEOMETRIES_PATH = "./.fig_geometries"


def freshfig(num=None, place=True, **kwargs):
    """Create/clear figure, place it, call `plt.subplots(**kwargs)`.

    If `figure(num)` exists, it is **cleared** before calling `subplots`.
    Unlike closing/opening, this keeps its position and size.

    If `place==2`, the figure placement is `load`ed, provided the figure's
    position has previously been `save`d. If `place==1`, the active placement
    only happens if the figure did not yet exist.

    .. note:
        Active placement (including re-sizing) on the `mpl` backend **MacOSX**
        [does not work](https://stackoverflow.com/a/30180994). However, sizing
        **upon creation** works, and Qt5Agg (or TkAgg) can also be installed.

    Example
    -------
    >>> freshfig(1, nrows=2, sharex=True)  # doctest: +NORMALIZE_WHITESPACE
    (<Figure size 640x480 with 2 Axes>,
    array([<AxesSubplot:>, <AxesSubplot:>], dtype=object))
    """
    already_open = plt.fignum_exists(num)

    fig = plt.figure(num=num, figsize=kwargs.pop("figsize", None))

    # Deal with warning bug
    # https://github.com/matplotlib/matplotlib/issues/9970
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        fig.clf()  # <=> fig.clear()

    if (
        is_using_interactive_backend()
        and place > 1 or (place and not already_open)
        and num is not None  # It makes little sense to load placement
                             # for the figure number resulting from None
    ):
        load(fignums=fig.number)

    _, ax = plt.subplots(num=fig.number, **kwargs)
    return fig, ax


def _get_fig(fignum=None):
    """Get fig handle from number OR handle."""
    if fignum is None:
        return plt.gcf()
    elif isinstance(fignum, mpl.figure.Figure):
        return fignum
    else:
        return plt.figure(fignum)


def _get_fmw(fignum):
    """If this fails, there's probs no way to make placement work."""
    # fmw = plt.get_current_fig_manager().window
    fig = _get_fig(fignum)
    fmw = fig.canvas.manager.window
    return fmw


def get_geo1(fignum):
    """Get geometry specification of a figure."""
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


def set_geo1(fignum, geo):
    """Set figure geometry."""
    plt.figure(fignum)
    try:
        fmw = _get_fmw(int(fignum))
    except AttributeError:
        # print("Could not place window with this mpl backend. Try Qt5Agg.")
        return
    try:
        # For Qt4Agg/Qt5Agg
        fmw.setGeometry(geo['x'], geo['y'], geo['w'], geo['h'])
    except Exception:
        # For TkAgg
        # geo = "{w:.0f}x{h:.0f}+{x:.0f}+{y:.0f}".format(**geo)
        fmw.geometry(newGeometry=geo)


def save(path=_FIG_GEOMETRIES_PATH, append_host=True):
    """Save current figure layout."""
    if append_host:
        path = ".".join([path, platform.node()])

    placements = {num: get_geo1(num) for num in plt.get_fignums()}

    with open(path, "w") as file:
        file.write(json.dumps(placements))


_HAS_NOTIFIED = False


def load(path=_FIG_GEOMETRIES_PATH, append_host=True, fignums=None):
    """Load/set figure layout."""
    if append_host:
        path = ".".join([path, platform.node()])

    global _HAS_NOTIFIED
    if not Path(path).is_file():
        if not _HAS_NOTIFIED:
            print(f"Note: for persistent figure layout use {__name__}.save().")
            _HAS_NOTIFIED = True
        return

    with open(path, "r") as file:
        placements = json.load(file)

    # Convert fignums to int
    for k in list(placements):
        placements[int(k)] = placements.pop(k)

    for num in placements:
        if fignums is None or num == fignums:
            set_geo1(num, placements[num])


def show_figs(fignums=None):
    """Move all fig windows to top.

    Doesn't work all that well for all backends/platforms.
    """
    # Validate fignums
    if fignums is None:
        fignums = plt.get_fignums()
    try:
        fignums = list(fignums)
    except TypeError:
        fignums = [fignums]

    for f in fignums:
        plt.figure(f)
        fmw = plt.get_current_fig_manager().window
        fmw.attributes('-topmost', 1)  # Bring to front, but
        fmw.attributes('-topmost', 0)  # don't keep in front


def get_screen_size():
    """Get **available** screen size/resolution.

    NB: This might not always work that well,
    especially since the method used depends on the backend.

    Consider using non-mpl method: https://pypi.org/project/screeninfo
    """
    if mpl.get_backend().startswith('Qt'):
        try:
            # Ref spyder/widgets/shortcutssummary.py
            from qtpy.QtWidgets import QDesktopWidget  # type: ignore
            widget = QDesktopWidget()
            sc = widget.availableGeometry(widget.primaryScreen())
            x0, y0, w0, h0 = sc.x(), sc.y(), sc.width(), sc.height()

        except ImportError:
            # https://stackoverflow.com/a/29039755/38281
            fig = plt.figure()  # new, blank (cheap to resize) figure
            mgr = plt.get_current_fig_manager()
            # Now we full-screen the new figure, and pause for effect.
            # NB: both of these actions results in the figure being shown.
            mgr.full_screen_toggle(); plt.pause(0.2)  # noqa
            sc = mgr.canvas
            x0, y0, w0, h0 = sc.x(), sc.y(), sc.width(), sc.height()
            # mgr.full_screen_toggle()
            plt.close(fig)

    elif mpl.get_backend() == "TkAgg":
        # https://stackoverflow.com/a/42951711/38281
        mgr = plt.get_current_fig_manager()
        x0, y0, w0, h0 = (0, 0) + mgr.window.wm_maxsize()
        # w, h = mgr.window.winfo_screenwidth(), mgr.window.winfo_screenheight()
    else:
        print("Warning: could not detect screen size for this mpl backend.")
        print("Using a default size.")
        x0, y0, w0, h0 = 30, 30, 800, 600

    return x0, y0, w0, h0


def loc01(fignum=None, x=None, y=None, w=None, h=None):
    """Place figure on screen, in relative coordinates ∈ [0, 1].

    Only works on Linux?
    """
    try:
        fmw = _get_fmw(fignum)
    except AttributeError:
        return  # do nothing

    x0, y0, w0, h0 = get_screen_size()

    # It seems the window footers are not taken into account
    # by the geometry settings. Correct for this:
    footer = 0.028*(h0+y0)

    # Current values (Qt4Agg only!):
    w = w if w is not None else fmw.width() / w0
    h = h if h is not None else fmw.height()/h0
    x = x if x is not None else fmw.x()     / w0
    y = y if y is not None else fmw.y()     / h0

    x = x0 + x*w0
    y = y0 + y*h0 + footer
    w = w*w0
    h = h*h0 - footer

    try:  # For Qt4Agg/Qt5Agg
        fmw.setGeometry(x, y, w, h)
    except: # noqa # For TkAgg
        geo = f"{int(w)}x{int(h)}+{int(x)}+{int(y)}"
        fmw.geometry(newGeometry=geo)


def loc(loc, fignum=None):
    """Place figure on screen.

    - loc: string that defines the figures new geometry, given either as
       * NW, E, ...
       * 4 digits (as str or int) to define grid M,N,i,j.

    Example
    -------
    >>> N = 3
    >>> for i in 1 + np.arange(N):
    ...     xy = str(N)*2 + str(i)*2
    ...     loc(xy, i)
    """
    loc = str(loc)
    loc = loc.replace(",", "")
    if not loc[:4].isnumeric():
        if loc.startswith('NW'):
            loc = '2211'
        elif loc.startswith('SW'):
            loc = '2221'
        elif loc.startswith('NE'):
            loc = '2212'
        elif loc.startswith('SE'):
            loc = '2222'
        elif loc.startswith('W'):
            loc = '1211'
        elif loc.startswith('E'):
            loc = '1212'
        elif loc.startswith('S'):
            loc = '2121'
        elif loc.startswith('N'):
            loc = '2111'

    # Split digits
    M, N = int(loc[0]), int(loc[1])
    if loc[3] == '-':
        i1, i2 = int(loc[2]), int(loc[4])
    else:
        i1, i2 = int(loc[2]), int(loc[2])
    if loc[-2] == '-':
        j1, j2 = int(loc[-3]), int(loc[-1])
    else:
        j1, j2 = int(loc[-1]), int(loc[-1])
    # Validate
    assert M >= i2 >= i1 > 0, "The specified col index is invalid."
    assert N >= j2 >= j1 > 0, "The specified row index is invalid."

    # Place
    di = i2-i1+1
    dj = j2-j1+1
    loc01(fignum, (j1-1)/N, (i1-1)/M, dj/N, di/M)
