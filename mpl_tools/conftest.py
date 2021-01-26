"""Configures pytest (beyond the ini file)."""
import numpy
import pytest


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    """Add numpy as np for doctests."""
    doctest_namespace["np"] = numpy
