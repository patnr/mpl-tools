import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.artist import allow_rasterization

from mpl_tools.misc import *

__all__ = ["align_ax_with", "anchor_axes", "set_ax_size"]

def set_ax_size(ax, w, h):
    "Width/Height in display (pixel) coords."
    fig = ax.figure
    w,h = fig.transFigure.inverted().transform([w,h])
    x,y,_,_ = ax.get_position().bounds
    ax.set_position([x,y,w,h])


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
    B = ax.bbox.anchored(loc.replace("+",""), container=bbox)
    # Adjust for + flags
    x,y,w,h = B.bounds
    if "W+" in loc: x+= bbox.width + pad
    if "E+" in loc: x-= bbox.width + pad
    if "S+" in loc: y-= h          + pad
    if "N+" in loc: y+= h          + pad
    B = mpl.transforms.Bbox.from_bounds(x,y,w,h)
    # Convert to figure coordinates
    B = B.inverse_transformed(ax.figure.transFigure)
    # Set
    ax.set_position(B)



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
        set_ax_size(self,*size)
        align_ax_with(self, get_anchor(), loc)
        _draw(renderer)
    _draw = ax.draw
    ax.draw = draw.__get__(ax)
