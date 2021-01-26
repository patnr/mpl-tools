"""Like test_log_toggler, but for sci.py."""

import numpy as np

from mpl_tools.sci import axes_with_marginals, cov_ellipse
from tests import comparison, init_fig


@comparison
def test_cov_ellipse():
    """Validate doctest's image output."""
    fig, ax = init_fig()
    # The rest is a copy of the doctest
    x, y = 10, 20
    _ = ax.set(xlim=(x-1, x+1), ylim=(y-1, y+1))
    _ = cov_ellipse(ax, (x, y), [[1, .3], [.3, 1]],
                    fc='none', ec='r', lw=4, label='$1\\sigma$')


@comparison
def test_axes_with_marginals():
    """Validate doctest's image output."""
    fig, ax = init_fig()
    # The rest is a copy of the doctest
    ax0, a_x, a_y = axes_with_marginals(4, 1)
    np.random.seed(0)
    x, y = np.random.randn(2, 500)
    _ = ax0.scatter(x, y)
    _ = a_x.hist(x)
    _ = a_y.hist(y, orientation="horizontal")
