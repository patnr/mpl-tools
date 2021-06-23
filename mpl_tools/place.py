"""Tools for placing figures (not axes) on screen."""
import functools
import json
import platform
import warnings
from pathlib import Path

import matplotlib as mpl
from matplotlib import pyplot as plt

from mpl_tools import is_notebook_or_qt, is_using_interactive_backend

_FIG_GEOMETRIES_PATH = "./.fig_layout"


@functools.wraps(warnings.warn)
def warn(*args, **kwargs):
    """Avoid warnings printing the source code for itself.

    For example, we don't want `warnings.warn("Something went wrong")`
    to print that whole source line, which would duplicate the actual message.
    Using the `stacklevel` arg of `warn` doesn't cut it, because we don't
    necessarily want to climb one level up.

    Refs:
    - <https://stackoverflow.com/a/26433913>
    - <https://stackoverflow.com/a/2187390>
    """
    kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1

    def frmt_warning(msg, category, filename, lineno, file=None, line=None):
        return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, msg)

    # Set custom frmt_warning (before calling warn), but restore original afterwards
    original = warnings.formatwarning
    warnings.formatwarning = frmt_warning
    warnings.warn(*args, **kwargs)
    warnings.formatwarning = original


def freshfig(num=None, place=True, rel=False, **kwargs):
    """Create/clear figure, place it, call `plt.subplots(**kwargs)`.

    If `figure(num)` exists, it is **cleared** before calling `subplots`.
    Unlike closing/opening, this keeps its position and size.
    Note that `num` can also be a string, i.e. the label of the figure.

    If `place==2`, the figure placement is `load`ed, provided the figure's
    position has previously been `save`d. If `place==1`, the active placement
    only happens if the figure did not yet exist.
    If `figsize` is among the `kwargs` it will still be overruled
    by the figure placement, as it should (it is quite convenient when
    working with scripts that *also* run in Jupyter).

    If `rel`, then `figsize` is multiplied by `rcParams["figure.figsize"]`,
    which can then be conveniently used to adjust all figure sizes.

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

    # Scale figsize
    figsize = kwargs.pop("figsize", None)
    if rel:
        w0, h0 = plt.rcParams["figure.figsize"]
        w, h = figsize
        figsize = w*w0, h*h0

    fig = plt.figure(num=num, figsize=figsize)

    # Deal with warning bug
    # https://github.com/matplotlib/matplotlib/issues/9970
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        fig.clf()  # <=> fig.clear()

    if (
        place > 1 or (place and not already_open)
        and num is not None  # It makes little sense to load placement
                             # for the figure number resulting from None
    ):
        load(fignum=num)

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


class FigManagerDoesNotExist(Exception):
    """Signal that figure placement ain't possible with this mpl backend.

    Use exception (a custom subclass for finesse and thereby safety) to
    propagate error up stack to where we want to treat them. Consider: the
    alternative solution of returning some special value to signal an error
    would necessitate an additional `if (val==SPECIAL): return SPECIAL` clause
    at each intervening-level, even for functions that are not supposed to
    return anything.
    """


def _get_fmw(fignum):
    fig = _get_fig(fignum)
    try:
        fmw = fig.canvas.manager.window
        # fmw = plt.get_current_fig_manager().window
    except AttributeError:
        raise FigManagerDoesNotExist(
            "Cannot programmatically manipulate figure windows"
            f" with the current mpl. backend ({mpl.get_backend()})")
    return fmw


def _get_geo1(fignum):
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


def _set_geo1(fignum, geo):
    fmw = _get_fmw(fignum)
    # For Qt4Agg/Qt5Agg
    try:
        return fmw.setGeometry(geo['x'], geo['y'], geo['w'], geo['h'])
    except Exception:
        pass
    # For TkAgg
    try:
        # geo = "{w:.0f}x{h:.0f}+{x:.0f}+{y:.0f}".format(**geo)
        return fmw.geometry(newGeometry=geo)
    except Exception:
        pass
    warn(f"Could not place figure {fignum}."
         f" Did you change the mpl backend?"
         f" Try deleting {_FIG_GEOMETRIES_PATH}")


def save(path=_FIG_GEOMETRIES_PATH, append_host=True):
    """Save current figure layout."""
    if append_host:
        path = ".".join([path, platform.node()])

    try:
        # Use labels if defined, else numbers
        lbls = [lbl or num for lbl, num in
                zip(plt.get_figlabels(), plt.get_fignums())]
        placements = {k: _get_geo1(k) for k in lbls}
    except FigManagerDoesNotExist as e:
        warn(str(e))
    else:
        # Get old placements
        if Path(path).is_file():
            with open(path, "r") as file:
                old = json.load(file)
        else:
            old = {}
        # Write old + new placements
        with open(path, "w") as file:
            file.write(json.dumps({**old, **placements}))


def load(path=_FIG_GEOMETRIES_PATH, append_host=True, fignum=None):
    """Load/set figure layout."""
    if is_notebook_or_qt or not is_using_interactive_backend():
        return  # quietly

    if append_host:
        path = ".".join([path, platform.node()])

    # Suggest saving layout
    if not Path(path).is_file():
        # TODO: deactivate until this is resolved:
        # https://stackoverflow.com/q/66388579
        # warn(f"Consider using {__name__}.save()"
        #      " for persistent figure layout.", stacklevel=2)
        return

    with open(path, "r") as file:
        placements = json.load(file)

    # Cast nums to int
    for key in list(placements):
        try:
            lbl = int(key)
        except ValueError:
            lbl = key
        placements[lbl] = placements.pop(key)

    try:
        for lbl in placements:
            if fignum is None or lbl == fignum:
                _set_geo1(lbl, placements[lbl])
    except FigManagerDoesNotExist as e:
        warn(str(e))


def show_figs(fignums=None):
    """Move all fig windows to top."""
    # Validate fignums
    if fignums is None:
        fignums = plt.get_fignums()
    try:
        fignums = list(fignums)
    except TypeError:
        fignums = [fignums]

    try:
        for f in fignums:
            fmw = _get_fmw(f)
            fmw.attributes('-topmost', 1)  # Bring to front, but
            fmw.attributes('-topmost', 0)  # don't keep in front
    except FigManagerDoesNotExist as e:
        warn(str(e))


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
    except FigManagerDoesNotExist as e:
        warn(str(e))
        return

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
