"""Science-related mpl tools."""

import matplotlib.colors
import matplotlib.ticker
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse
from numpy.linalg import eigh

from mpl_tools.place import freshfig


def cov_ellipse(ax, mu, sigma, **kwargs):
    r"""Draw ellipse corresponding to (Gaussian) 1-sigma countour of cov matrix.

    [Inspiration](https://stackoverflow.com/q/17952171)

    Example
    -------
    >>> fig, ax = plt.subplots()
    >>> x, y, C = 10, 20, [[1, .3], [.3, 1]]
    >>> _ = ax.set(xlim=(x-1, x+1), ylim=(y-1, y+1))
    >>> ellipse = cov_ellipse(ax, (x, y), C,
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


def matshow_discrete(X, fig_ax=None, cmap=None, mode="set", ndigits=8):
    """Do matshow, add **discrete colorbar**.

    Inspired by https://stackoverflow.com/a/60870122

    Example:
    >>> from scipy import sparse
    >>> D = sparse.diags([1, -2, 1], [-1, 0, 1], shape=(9, 9))
    >>> image, colorbar = matshow_discrete(D.A)
    """
    if isinstance(fig_ax, str):
        fig, ax = freshfig(fig_ax)
    elif fig_ax is None:
        fig, ax = freshfig("matshow_discrete")
    else:
        fig, ax = fig_ax

    X = np.asarray(X)
    m, M = X.min(), X.max()

    # Default cmap
    if cmap is None:
        if M == 0:
            cmap = "cool"
        elif m == 0:
            cmap = "autumn"
        elif m < 0 and M > 0:
            cmap = "coolwarm"
        else:
            cmap = "jet"

    if mode == "set":
        # Get unique, sorted list of values
        S = np.round(X, ndigits)
        S = set(S.flat)  # unique
        S = np.array(sorted(S))
        # Get boundaries below and above each value of S
        # (the exact amount of these margins don't matter).
        bins = (S[1:] + S[:-1])/2
        bins = np.concatenate(([m-1], bins, [M+1]))
        # Center ticks (vs bins)
        ticks = bins[:-1] + np.diff(bins)/2
        # Custom tick labels
        formatter = matplotlib.ticker.FuncFormatter(
            lambda x, idx: "None" if idx is None else "%.2f" % S[idx])  # type: ignore
        # Create cmap and norm
        if cmap == "coolwarm":
            # Ensure 0 corresponds to .5
            neg = np.linspace(0, .5, np.sum(S < 0) + 1)[:-1]
            pos = np.linspace(.5, 1, np.sum(S > 0) + 1)[1:]
            xx = np.concatenate([neg, [.5], pos])
        else:
            xx = np.linspace(0, 1, len(S))
        cmap = plt.get_cmap(cmap)(xx)
        cmap = matplotlib.colors.ListedColormap(cmap)
        norm = matplotlib.colors.BoundaryNorm(bins, cmap.N)

        im = ax.matshow(X, cmap=cmap, norm=norm)
        cb = fig.colorbar(im, ticks=ticks, format=formatter)

    elif mode == "linear":
        nlevels = 11
        ticks = np.linspace(m, M, nlevels)
        cmap = plt.get_cmap(cmap, nlevels)
        im = ax.matshow(X, cmap=cmap,
                        # Center outer ticks by stretching map
                        vmin=1.5*ticks[0] - .5*ticks[1],
                        vmax=1.5*ticks[-1] - .5*ticks[-2])
        cb = fig.colorbar(im, ticks=ticks)

    else:
        raise ValueError("Invalid mode.")

    return im, cb


def matshow_banded(bands, fig_ax=None, lower=True):
    """Plot matrix with `bands` as in `solveh_banded`, using `matshow_discrete`.

    Example:
    >>> bands = np.zeros((2, 10-2))
    >>> bands[0] = 2
    >>> bands[1, :-1] = -1
    >>> image, colorbar = matshow_banded(bands)
    """
    if not lower:
        raise NotImplementedError

    m = bands.shape[-1]
    D = np.zeros((m, )*2)
    for i, band in enumerate(bands):
        c = 1 if i else .5
        D += c * np.diag(band[:m-i], k=i)
    D += D.T

    return matshow_discrete(D, fig_ax)
