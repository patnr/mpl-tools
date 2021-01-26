"""Toggle visisbility of plot elements on/off. Provide checkmarks for it."""
import itertools
import textwrap
import warnings

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import transforms as mtransforms
from matplotlib.widgets import CheckButtons


def toggle_lines(ax=None, autoscl=True, numbering=False,
                 txtwidth=15, txtsize=None, state=None):
    """Make checkbuttons to toggle visibility of each line in current plot.

    - `autoscl`  : Rescale axis limits as required by currently visible lines.
    - `numbering`: Add numbering to labels.
    - `txtwidth` : Wrap labels to this length.

    The state of checkboxes can be inquired by
    >>> OnOff = [lh.get_visible() for lh in # doctest: +SKIP
    ...          ax.findobj(lambda x: isinstance(x,mpl.lines.Line2D))[::2]]
    """
    if ax is None:
        ax = plt.gca()
    if txtsize is None:
        txtsize = mpl.rcParams['font.size']

    # Get lines and their properties
    lines = {'handle': list(ax.get_lines())}
    for prop in ['label', 'color', 'visible']:
        lines[prop] = [plt.getp(x, prop) for x in lines['handle']]

    # Rm those that start with _
    not_ = [not x.startswith('_') for x in lines['label']]
    for prop in lines:
        lines[prop] = list(itertools.compress(lines[prop], not_))
    N = len(lines['handle'])

    # Adjust labels
    if numbering:
        lines['label'] = [str(i) + ': ' + x for i, x in enumerate(lines['label'])]
    if txtwidth:
        lines['label'] = [textwrap.fill(x, width=txtwidth) for x in lines['label']]

    # Set state. BUGGY? sometimes causes MPL complaints after clicking boxes
    if state is not None:
        state = np.array(state).astype(bool)
        lines['visible'] = state
        for i, x in enumerate(state):
            lines['handle'][i].set_visible(x)

    # Setup buttons
    # When there's many, the box-sizing is awful, but difficult to fix.
    W = 0.23 * txtwidth / 15 * txtsize / 10
    nBreaks = sum(x.count('\n') for x in lines['label'])  # count linebreaks
    H = min(1, 0.05 * (N + nBreaks))
    plt.subplots_adjust(left=W + 0.12, right=0.97)
    rax = plt.axes([0.05, 0.5 - H / 2, W, H])
    check = CheckButtons(rax, lines['label'], lines['visible'])

    # Adjust button style
    for i in range(N):
        check.rectangles[i].set(lw=0, facecolor=lines['color'][i])
        check.labels[i].set(color=lines['color'][i])
        if txtsize:
            check.labels[i].set(size=txtsize)

    # Callback
    def toggle_visible(label):
        ind    = lines['label'].index(label)
        handle = lines['handle'][ind]
        vs     = not lines['visible'][ind]
        handle.set_visible(vs)
        lines['visible'][ind] = vs
        if autoscl:
            _autoscale_based_on(ax, list(itertools.compress(
                lines['handle'], lines['visible'])))
        plt.draw()
    check.on_clicked(toggle_visible)

    # Return focus
    plt.sca(ax)

    # Must return (and be received) so as not to expire.
    return check


# https://stackoverflow.com/a/7396313
def _autoscale_based_on(ax, line_handles):
    """Autoscale axis based (only) on `line_handles`."""
    ax.dataLim = mtransforms.Bbox.unit()
    for iL, lh in enumerate(line_handles):
        xy = np.vstack(lh.get_data()).T
        ax.dataLim.update_from_data_xy(xy, ignore=(iL == 0))
    ax.autoscale_view()


def toggle_viz(*handles, prompt=False, legend=False, pause=0.0):
    """Toggle visibility of the graphics with handle `handles`."""
    are_viz = []
    for h in handles:

        # Core functionality: turn on/off
        is_viz = not h.get_visible()
        h.set_visible(is_viz)
        are_viz += [is_viz]

        # Legend updating. Basic version: works by
        #  - setting line's label (to /'_nolegend_' if off)
        #  - re-calling legend()
        if legend:
            if is_viz:
                try:
                    h.set_label(h.actual_label)
                except AttributeError:
                    pass
            else:
                h.actual_label = h.get_label()
                h.set_label('_nolegend_')
            # Legend refresh
            ax = h.axes
            with warnings.catch_warnings():
                warnings.simplefilter("error", category=UserWarning)
                try:
                    ax.legend()
                except UserWarning:
                    # If all labels are '_nolabel_' then ax.legend() throws warning,
                    # and quits before refreshing.
                    # => Refresh by creating/rm another legend.
                    ax.legend('TMP').remove()

    # Pause at where used (typically sequentially in script)
    if prompt:
        input("Press <Enter> to continue...")
    if pause > 0:
        plt.pause(pause)

    return are_viz
