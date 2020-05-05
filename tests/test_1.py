# -*- coding: utf-8 -*-

# import pytest

import matplotlib as mpl
from matplotlib import pyplot as plt

from mpl_tools import *


def show(fig):
    # https://stackoverflow.com/q/35403127/#comment106377020_48728877
    BE = mpl.get_backend().lower()
    if BE=="agg":
        plt.draw()
        fig.savefig("tmp.pdf")
    else:
        plt.show(block=False)
        plt.pause(.5)


def test_log_toggling():

    fig, ax = freshfig(1)
    K = 5
    for i in range(K):
        ax.plot([0,K], [6**x for x in [-2,i]], label=i)
    ax.legend()
    add_log_toggler(ax)

    show(fig)
    toggle_scale(ax)
    show(fig)
    toggle_scale(ax)
    show(fig)

    assert 2==2
