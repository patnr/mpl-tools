from matplotlib.widgets import Button, CheckButtons

from mpl_tools.misc import *


def add_log_toggler(ax, button_ax, ylim=None):
    """Add button that toggles log. scale."""

    # ax.toggle_log = Button(button_ax, 'Toggle scale',color="w")

    ax.toggle_log = CheckButtons(button_ax, ["Log scale"], [False])
    dh = .3
    for box,cross in zip(ax.toggle_log.rectangles,ax.toggle_log.lines):
        box.set_y(dh)
        box.set_height(1-2*dh)
        cross[0].set_ydata([dh,1-dh])
        cross[1].set_ydata([dh,1-dh][::-1])

    toggler = lambda _: toggle_scale(ax,ylim)
    ax.toggle_log.on_clicked(toggler)


def toggle_scale(ax,ylim=None):
    "Toggle log. scale."

    # Get current status -- button
    if isinstance(ax.toggle_log, mpl.widgets.Button):
        log_is_on = getattr(ax,"_log_is_on",False)
        ax._log_is_on = not log_is_on

        if log_is_on:
            # ax.toggle_log.label.set_text("Log. scale: Off")
            ax.toggle_log.color = "w"
        else:
            # ax.toggle_log.label.set_text("Log. scale: On")
            ax.toggle_log.color = "#D5F2E8"

    # Get current status -- Checkmark
    elif isinstance(ax.toggle_log, mpl.widgets.CheckButtons):
        log_is_on = not ax.toggle_log.get_status()[0]
    else:
        raise TypeError

    # Toggle
    if log_is_on:
        ax.set_yscale("linear")
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(thousands)
    else:
        ax.autoscale(True,axis="y")
        if ylim: ax.set_ylim(ylim)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(thousands)
    plt.draw()
