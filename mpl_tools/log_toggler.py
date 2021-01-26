"""Toggle log-scale on and off. Provide button for it."""
import warnings

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.widgets import CheckButtons  # Button

from mpl_tools.ax_placement import anchor_axes, get_legend_bbox
from mpl_tools.misc import thousands


def add_log_toggler(ax, pos="leg:S+W", ylim=None):
    """Add button that toggles log. scale."""
    fig = ax.figure

    if mpl.get_backend() == "Qt5Agg":
        print("Warning: Qt5Agg is used, which is not very fast with this function")

    # button_ax: size and creation
    size = _xFontsize(mpl.rcParams['font.size'], fig, 10, 2.5)
    size = fig.transFigure.inverted().transform(size)
    rect = [.5, .5, *size]
    button_ax = fig.add_axes(rect, frameon=False, xticks=[], yticks=[])
    # button_ax: position
    if "leg:" in pos:
        pos = pos.replace("leg:", "")
        # Continuous re-positioning:
        anchor_axes(button_ax, get_legend_bbox(ax), pos)
        # Position once only (will scale with figure):
        # align_ax_with(button_ax, get_legend_bbox(ax)(), "NW+")
    else:
        anchor_axes(button_ax, lambda: ax.bbox, "NE")

    # Create button/checkmarks
    ax.log_toggler = CheckButtons(button_ax, ["Log scale"], [False])
    # Adjust checkmark style
    dh = .3
    for box, cross in zip(ax.log_toggler.rectangles, ax.log_toggler.lines):
        box.set_y(dh)
        box.set_height(1 - 2 * dh)
        cross[0].set_ydata([dh, 1 - dh])
        cross[1].set_ydata([dh, 1 - dh][::-1])

    # Set callback
    def toggler(_):
        return toggle_scale(ax, ylim, _toggle_button=False)
    ax.log_toggler.on_clicked(toggler)


def toggle_scale(ax, ylim=None, formatter=thousands, _toggle_button=True):
    """Toggle log. scale.

    _toggle_button is used internally. Do not set.
    """
    # Get status
    log_is_on = getattr(ax, "_log_is_on", False)

    # Toggle button
    # NB: Setting the active status of the button
    # will call this same function,
    # but with _toggle_button=False.
    if _toggle_button and hasattr(ax, "log_toggler"):
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
            ax.autoscale(True, axis="y")
            if ylim:
                ax.set_ylim(ylim)
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(formatter)
        plt.draw()


def _xFontsize(fontsize, fig, *args):
    """Multiply by fontsize, in pixels (rather than points)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        plt.pause(.1)
    fontsize = fig.canvas.renderer.points_to_pixels(fontsize)
    return tuple(a * fontsize for a in args)
