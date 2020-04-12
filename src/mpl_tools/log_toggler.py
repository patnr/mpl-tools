import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, CheckButtons

from mpl_tools.ax_placement import anchor_axes
from mpl_tools.misc import get_legend_bbox, thousands, xFontsize

__all__ = ["add_log_toggler", "toggle_scale"]

def add_log_toggler(ax, pos="leg:S+W", ylim=None):
    """Add button that toggles log. scale."""
    fig = ax.figure

    # button_ax: size and creation
    size = xFontsize(mpl.rcParams['font.size'],fig,10,2.5)
    size = fig.transFigure.inverted().transform(size)
    rect = [.5,.5, *size]
    button_ax = fig.add_axes(rect, frameon=False, xticks=[], yticks=[])
    # button_ax: position
    if "leg:" in pos:
        pos = pos.replace("leg:","")
        # Continuous re-positioning:
        anchor_axes(button_ax, get_legend_bbox(ax), pos)
        # Position once-only (will scale with figure):
        # align_ax_with(button_ax, get_legend_bbox(ax)(), "NW+")
    else:
        anchor_axes(button_ax, lambda: ax.bbox , "NE")

    # Create button/checkmarks
    ax.log_toggler = CheckButtons(button_ax, ["Log scale"], [False])
    # Adjust checkmark style
    dh = .3
    for box,cross in zip(ax.log_toggler.rectangles,ax.log_toggler.lines):
        box.set_y(dh)
        box.set_height(1-2*dh)
        cross[0].set_ydata([dh,1-dh])
        cross[1].set_ydata([dh,1-dh][::-1])

    # Set callback
    toggler = lambda _: toggle_scale(ax,ylim,_toggle_button=False)
    ax.log_toggler.on_clicked(toggler)


def toggle_scale(ax,ylim=None,formatter=thousands,_toggle_button=True):
    """Toggle log. scale.

    _toggle_button is used internally. Do not set.
    """

    # Get status
    log_is_on = getattr(ax,"_log_is_on",False)

    # Toggle button
    # NB: Setting the active status of the button
    # will call this same function,
    # but with _toggle_button=False.
    if _toggle_button and hasattr(ax,"log_toggler"):
        ax.log_toggler.set_active(0)

    else:
        # Toggle scale
        ax._log_is_on = not log_is_on
        if log_is_on:
            ax.set_yscale("linear")
            ax.set_ylim(bottom=0)
            ax.yaxis.set_major_formatter(formatter)
        else:
            ax.set_yscale("linear")
            ax.autoscale(True,axis="y")
            if ylim: ax.set_ylim(ylim)
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(formatter)
        plt.draw()
