# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

from mpl_tools.ax_placement import *
from mpl_tools.log_toggler import *
from mpl_tools.misc import *

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'mpl-tools'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound, dist_name
