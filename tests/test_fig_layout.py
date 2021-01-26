"""Test misc.py"""
import matplotlib as mpl
from matplotlib import pyplot as plt

import mpl_tools.fig_layout as fig_layout


def test_fig_placement():
    """Test `save == load`."""

    bk = mpl.get_backend()
    mpl.use("Qt5Agg")

    fig, ax = plt.subplots(1)
    geo1 = fig_layout.get_geo1(1)
    fig_layout.save()

    plt.close("all")

    fig, ax = plt.subplots(1)
    fig_layout.load()
    geo2 = fig_layout.get_geo1(1)

    mpl.use(bk)
    assert geo1 == geo2
