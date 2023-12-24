# types.py

from draftsman.entity import Locomotive, CargoWagon, FluidWagon, ArtilleryWagon
from draftsman.entity import TransportBelt, UndergroundBelt, Splitter

from typing import Union


RollingStock = Union[Locomotive, CargoWagon, FluidWagon, ArtilleryWagon]

Belts = Union[TransportBelt, UndergroundBelt, Splitter]
