# __init__.py
"""
Docstring
"""
# Remember: objects with a preceding '_' are ignored by the module manager
from factoriotools._version import __version__, __version_info__
from factoriotools._factorio_version import __factorio_version__, __factorio_version_info__

# TODO: make a defines file
NORTH = 0
NORTHEAST = 1
EAST = 2
SOUTHEAST = 3
SOUTH = 4
SOUTHWEST = 5
WEST = 6
NORTHWEST = 7

from factoriotools.utils import *
from factoriotools.signals import *
from factoriotools.entity import *
from factoriotools.blueprint import *