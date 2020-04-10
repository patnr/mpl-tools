# -*- coding: utf-8 -*-

# import pytest

from mpl_tools import *


def test_1():
    fig, ax = freshfig(1)
    K = 5
    for i in range(K):
        ax.plot([0,K], [0,i], label=i)
    ax.legend()

    size = xFontsize(10,fig,10,2)
    size = fig.transFigure.inverted().transform(size)
    ax2 = fig.add_axes([.5,.5,*size],frameon=True, xticks=[], yticks=[], facecolor="b")
    ax2.patch.set_alpha(0.1)

    # Once:
    # align_ax_with(ax2, get_legend_bbox(ax)(), "NW+")
    # Continuous:
    anchor_axes(ax2, get_legend_bbox(ax), "S+W")
    # anchor_axes(ax2, lambda: ax.bbox , "NE")

    add_log_toggler(ax, ax2)

    # Call plt.show(), which blocks, so that
    # the axes re-positioning gets called,
    # but close after an interval of time.
    # https://stackoverflow.com/a/30365738/38281
    def close_event():
        plt.close()
    timer = fig.canvas.new_timer(interval=2000)
    timer.add_callback(close_event)
    timer.start()
    plt.show()

    assert 2==2
