"""Run tests with pytest.

[Ref](https://matplotlib.org/3.1.1/devel/testing.html)

Whenever something changes, the corresponding test will fail.
If a test fails, the **difference to the baseline** may be inspected
by opening `result_images/my_test_module/test_name-failed-diff.png`.

Failure also happens when **adding new tests**.
To fix this (and complete the addition of the new test),
copy the png file (not "-expected.png")
from `result_images/my_test_module/`
into `tests/baseline_images/my_test_module/`.
Then, the next time, the test will succeed.
"""

from matplotlib.testing.decorators import image_comparison, check_figures_equal

import matplotlib as mpl
import matplotlib.pyplot as plt

from mpl_tools.log_toggler import add_log_toggler, toggle_scale

import warnings
from pytest import PytestUnknownMarkWarning as warning


class suppress_w(object):
    """Turn off warning due to something in `image_comparison`."""
    def __enter__(self):
        warnings.simplefilter("ignore", warning)
    def __exit__(self, type, value, traceback):
        warnings.simplefilter("default", warning)


def comparison(fun):
    """Convenience wrapper to `image_comparison` which automates naming."""
    name = fun.__name__.split("test_")[1]

    wrapper = image_comparison(baseline_images=[name],
                               remove_text=False, extensions=['pdf'])

    with suppress_w():
        fun = wrapper(fun)

    return fun


def gen_plot(fig=None):
    """Generate base plot."""

    # Cleanup from previous tests. Don't know why this isn't in image_comparison.
    # Clearly, cleanup is part of the code in mpl/testing/decorators.py
    plt.close("all")

    if fig is None:
        fig, ax = plt.subplots()
    else:
        ax = fig.subplots()

    nLines = 5
    for i in range(nLines):
        ax.plot([0, 1], [6**x for x in [-2, i]], label=i)
    plt.legend()

    return fig, ax


@comparison
def test_1():
    fig, ax = gen_plot()


@comparison
def test_2():
    fig, ax = gen_plot()
    add_log_toggler(ax)


@comparison
def test_3():
    fig, ax = gen_plot()
    add_log_toggler(ax)
    toggle_scale(ax)


@comparison
def test_4():
    fig, ax = gen_plot()
    add_log_toggler(ax)
    toggle_scale(ax)
    toggle_scale(ax)


# This test doesn't require a saved baseline image,
# and was supposed to replace test_4, coz both test toggle the scale twice,
# and presumably that would yield the original image.
# But, toggle_scale actually sets custom formatter and ylim, and so therefore it fails.
# @check_figures_equal(extensions=('pdf',))
# def test_5(fig_test, fig_ref):
#     _, ax1 = gen_plot(fig_ref)
#     _, ax2 = gen_plot(fig_test)
#     toggle_scale(ax2)
#     toggle_scale(ax2)
