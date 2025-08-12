# types.py

from draftsman.entity import Locomotive, CargoWagon, FluidWagon, ArtilleryWagon
from draftsman.entity import TransportBelt, UndergroundBelt, Splitter


RollingStock = Locomotive | CargoWagon | FluidWagon | ArtilleryWagon

Belts = TransportBelt | UndergroundBelt | Splitter
