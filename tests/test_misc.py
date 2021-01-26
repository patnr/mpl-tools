"""Test misc.py"""
from packaging import version

import mpl_tools
from mpl_tools.misc import axprops


def test_version():
    """Ensure semantic versioning in use."""
    try:
        version.parse(mpl_tools.__version__)
        assert True
    except version.InvalidVersion:
        raise AssertionError


def test_axprops():
    p2 = axprops(dict(xlabel="x", zlabel="z", ylim=(2, 3), color="red"))
    assert set(p2) == {"xlabel", "zlabel", "ylim"}
