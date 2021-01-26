"""Science-related mpl tools."""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse
from numpy.linalg import eigh


def cov_ellipse(ax, mu, sigma, **kwargs):
    r"""Draw ellipse corresponding to (Gaussian) 1-sigma countour of cov matrix.

    [Inspiration](https://stackoverflow.com/q/17952171)

    Example
    -------
    >>> fig, ax = plt.subplots()
    >>> x, y = 10, 20
    >>> _ = ax.set(xlim=(x-1, x+1), ylim=(y-1, y+1))
    >>> ellipse = cov_ellipse(ax, (x, y), [[1, .3], [.3, 1]],
    ...                       fc='none', ec='r', lw=4, label='$1\\sigma$')
    """
    # Cov --> Width, Height, Theta
    vals, vecs = eigh(sigma)
    x, y = vecs[:, -1]  # x-y components of largest (last) eigenvector
    theta = np.degrees(np.arctan2(y, x))
    theta = theta % 180

    h, w = 2 * np.sqrt(vals.clip(0))

    # Get artist
    e = Ellipse(mu, w, h, theta, **kwargs)

    ax.add_patch(e)
    e.set_clip_box(ax.bbox)  # why is this necessary?

    # Return artist
    return e


def axes_with_marginals(n_joint, n_marg, **kwargs):
    """Create a joint axis along with two marginal axes.

    Example
    -------
    >>> ax0, a_x, a_y = axes_with_marginals(4, 1)
    >>> x, y = np.random.randn(2,500)
    >>> _ = ax0.scatter(x,y)
    >>> _ = a_x.hist(x)
    >>> _ = a_y.hist(y,orientation="horizontal")
    """
    N = n_joint + n_marg

    # Method 1
    # fig, ((ax0, a_y), (a_x, _)) = plt.subplots(2,2,num=plt.gcf().number,
    # sharex='col',sharey='row',gridspec_kw={
    #     'height_ratios':[n_joint,n_marg],
    #     'width_ratios' :[n_joint,n_marg]})
    # _.set_visible(False) # Actually removing would bug the axis ticks etc.

    # Method 2
    gs   = GridSpec(N, N, **kwargs)
    fig  = plt.gcf()
    ax0 = fig.add_subplot(gs[n_marg:N, 0:n_joint])
    a_x = fig.add_subplot(gs[0:n_marg, 0:n_joint], sharex=ax0)
    a_y = fig.add_subplot(gs[n_marg:N, n_joint:N], sharey=ax0)
    # Cannot delete ticks coz axis are shared
    plt.setp(a_x.get_xticklabels(), visible=False)
    plt.setp(a_y.get_yticklabels(), visible=False)

    return ax0, a_x, a_y
