"""Run tests with pytest.

[Ref](https://matplotlib.org/3.1.1/devel/testing.html)

Whenever something changes, the corresponding test will fail.
If a test fails, the **difference to the baseline** may be inspected
by opening `result_images/my_test_module/test_name-failed-diff.png`.

If you're using a different extension that `.png`,
then the images will be converted to `.png` before comparison.
Also note that **travis** does not support `.png` comparison.

Failure also happens when **adding new tests**.
To fix this (and complete the addition of the new test),
copy the png file (not "-expected.png")
from `result_images/my_test_module/`
into `tests/baseline_images/my_test_module/`.
Then, the next time, the test will succeed.
"""
import warnings

import matplotlib as mpl
from matplotlib.testing.decorators import image_comparison
from pytest import PytestUnknownMarkWarning

mpl.use("agg")
import matplotlib.pyplot as plt  # noqa


class SuppressWarn(object):
    """Turn off warning due to something in `image_comparison`."""

    def __enter__(self):
        warnings.simplefilter("ignore", PytestUnknownMarkWarning)

    def __exit__(self, type_, value, traceback):
        warnings.simplefilter("default", PytestUnknownMarkWarning)


def comparison(fun):
    """Wrap `image_comparison` to make naming conveniently automatic."""
    name = fun.__name__.split("test_")[1]

    wrapper = image_comparison(baseline_images=[name],
                               remove_text=False, extensions=['png'])

    with SuppressWarn():
        fun = wrapper(fun)

    return fun


def init_fig(fig=None):
    """Cleanup from previous tests. Don't know why this isn't in image_comparison.

    Clearly, cleanup is part of the code in mpl/testing/decorators.py.
    """
    plt.close("all")
    if fig is None:
        fig, ax = plt.subplots()
    else:
        ax = fig.subplots()
    return fig, ax


def plot_lines(fig=None, nLines=5):
    """Generate base plot."""
    fig, ax = init_fig(fig)
    lines = []
    for i in range(nLines):
        ll = ax.plot([0, 1], [6**x for x in [-2, i]], label=i)
        lines.extend(ll)
    ax.legend()
    return fig, ax, lines
