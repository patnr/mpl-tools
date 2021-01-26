"""Test log_toggler.py."""
from mpl_tools.log_toggler import add_log_toggler, toggle_scale
from tests import comparison, plot_lines


@comparison
def test_1():
    """Initial test."""
    fig, ax, _ = plot_lines()


@comparison
def test_2():
    """Test with toggler added."""
    fig, ax, _ = plot_lines()
    add_log_toggler(ax)


@comparison
def test_3():
    """Test with log-scale."""
    fig, ax, _ = plot_lines()
    add_log_toggler(ax)
    toggle_scale(ax)


@comparison
def test_4():
    """Test with log-scale removed."""
    fig, ax, _ = plot_lines()
    add_log_toggler(ax)
    toggle_scale(ax)
    toggle_scale(ax)


# This test doesn't require a saved baseline image,
# and was supposed to replace test_4, coz both test toggle the scale twice,
# and presumably that would yield the original image.
# But, toggle_scale actually sets custom formatter and ylim, and so therefore it fails.
# @check_figures_equal(extensions=('png',))
# def test_5(fig_test, fig_ref):
#     _, ax1 = plot_lines(fig_ref)
#     _, ax2 = plot_lines(fig_test)
#     toggle_scale(ax2)
#     toggle_scale(ax2)
