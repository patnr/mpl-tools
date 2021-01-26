"""Test visibility.py"""

from mpl_tools.visibility import toggle_lines, toggle_viz
from tests import comparison, plot_lines


@comparison
def test_viz_1():
    fig, ax, lines = plot_lines()


@comparison
def test_viz_2():
    fig, ax, lines = plot_lines()
    toggle_viz(*lines)


@comparison
def test_viz_3():
    fig, ax, lines = plot_lines()
    toggle_viz(*lines, legend=True)


@comparison
def test_viz_4():
    fig, ax, lines = plot_lines()
    toggle_viz(*lines[1:], legend=True)


@comparison
def test_checks_1():
    fig, ax, lines = plot_lines()
    toggle_lines(ax, autoscl=True)
