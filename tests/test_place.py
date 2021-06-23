"""Test misc.py"""
import matplotlib as mpl
from matplotlib import pyplot as plt

import mpl_tools.place as place


def test_save_load():
    """Test `save == load`."""

    bk = mpl.get_backend()
    try:
        mpl.use("Qt5Agg")
    except ImportError:
        return

    fig, ax = plt.subplots(1)
    geo1 = place._get_geo1(1)
    place.save()

    plt.close("all")

    fig, ax = plt.subplots(1)
    place.load()
    geo2 = place._get_geo1(1)

    mpl.use(bk)
    assert geo1 == geo2
