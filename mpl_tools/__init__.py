from importlib.metadata import version
from pathlib import Path

try:
    __version__ = version(__name__)
except:
    pass
