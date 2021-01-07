from importlib.metadata import version
from pathlib import Path

import matplotlib as mpl

from mpl_tools.ax_placement import *
from mpl_tools.log_toggler import *
from mpl_tools.misc import *

try:
    __version__ = version(__name__)
except:
    pass
