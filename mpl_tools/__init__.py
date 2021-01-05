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


if mpl.get_backend()=="Qt5Agg":
    print("Warning: Qt5Agg is used",
          "which has been known to cause slow-down with",
          Path(__file__).parent.resolve())
