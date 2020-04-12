import matplotlib as mpl
from matplotlib import pyplot as plt

__all__ = ["thousands", "freshfig", "get_legend_bbox", "xFontsize"]

thousands = mpl.ticker.StrMethodFormatter('{x:,.7g}')

def freshfig(num=None,figsize=None,*args,**kwargs):
    """Create/clear figure.

    Similar to::

      fig, ax = suplots(*args,**kwargs)

    With the modification that:

    - If the figure does not exist: create it.
      This allows for figure sizing -- even with mpl backend MacOS.
    - Otherwise: clear figure.
      Avoids closing/opening so as to keep pos and size.
    """
    exists = plt.fignum_exists(num)

    fig = plt.figure(num=num,figsize=figsize)
    fig.clear()

    _, ax = plt.subplots(num=fig.number,*args,**kwargs)
    return fig, ax

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


def xFontsize(fontsize,fig,*args):
    """Multiply by fontsize, in pixels (rather than points)."""
    plt.pause(.1)
    fontsize = fig.canvas.renderer.points_to_pixels(fontsize)
    return tuple(a*fontsize for a in args)
