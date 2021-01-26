"""Tools for placing axes in a figure."""
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.artist import allow_rasterization

# from mpl_tools.misc import *

__all__ = ["align_ax_with", "anchor_axes", "set_ax_size", "trans2fig"]


def set_ax_size(ax, w, h):
    """Width/Height in display (pixel) coords."""
    fig = ax.figure
    w, h = fig.transFigure.inverted().transform([w, h])
    x, y, _, _ = ax.get_position().bounds
    ax.set_position([x, y, w, h])


def align_ax_with(ax, bbox, loc, pad=4):
    """Set the location of ax relative to bbox.

    This is similar to legend placement, where bbox_to_anchor
    (here just bbox) defines the anchor position (as a box),
    and loc specifies the relative placement as the edge(s) to be aligned.

    However, here, loc should be one of NW, NE, SW, SE, E, W, N, S (as in Matlab),
    and each letter may appended by ``+`` (e.g. N+W+),
    meaning that the edge of ax is placed
    *outside* the opposite edge of (the container) bbox,
    with padding specified by pad.
    """
    # Get new bbox placed with mpl builtin tool
    B = ax.bbox.anchored(loc.replace("+", ""), container=bbox)
    # Adjust for + flags
    x, y, w, h = B.bounds
    if "W+" in loc:
        x += pad + bbox.width
    if "E+" in loc:
        x -= pad + bbox.width
    if "S+" in loc:
        y -= pad + h
    if "N+" in loc:
        y += pad + h
    B = mpl.transforms.Bbox.from_bounds(x, y, w, h)
    # Convert to figure coordinates
    # B = B.inverse_transformed(ax.figure.transFigure) # deprecated
    B = B.transformed(ax.figure.transFigure.inverted())
    # Set
    ax.set_position(B)


# TODO: make use of this in the above funcs
def trans2fig(axis, rect, from_data=True):
    """Transform (data or axis) coordinates to figure coordinates.

    Inspired by: https://stackoverflow.com/a/17478227/38281.

    Example
    -------
    >>> rect = trans2fig(ax, [x,y,w,h]) # doctest: +SKIP
    ... ax2 = ax.figure.add_axes(rect)
    """
    x, y, w, h = rect

    FT = axis.figure.transFigure.inverted().transform

    if from_data:
        # Transform: data-->display-->figure
        def T(xy):
            return FT(axis.transData.transform(xy))
    else:
        # Transform: axes-->display-->figure
        def T(xy):
            return FT(axis.transAxes.transform(xy))

    x, y = T((x, y))
    w, h = T([w, h]) - T([0, 0])  # affine transform wrt. 0

    return x, y, w, h


def anchor_axes(ax, get_anchor, loc="NW+"):
    """Attach axes to an anchoring bbox, and keep its size fixed.

    This is done by updating its placement whenever draw() is called,
    e.g. when the figure is resized.

    See also mpl_toolkits.axes_grid1.{Divider,Size}, demonstrated by:
    https://matplotlib.org/gallery/axes_grid1/demo_fixed_size_axes.html
    """
    # Save size
    size = ax.bbox.width, ax.bbox.height

    # Patch the Axes instance's draw() method.
    @allow_rasterization
    def draw(self, renderer):
        set_ax_size(self, *size)
        align_ax_with(self, get_anchor(), loc)
        _draw(renderer)
    _draw = ax.draw
    ax.draw = draw.__get__(ax)


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
