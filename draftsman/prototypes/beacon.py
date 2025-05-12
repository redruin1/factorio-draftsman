# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    ItemRequestMixin,
    EnergySourceMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import beacons

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class Beacon(ModulesMixin, ItemRequestMixin, EnergySourceMixin, Entity):
    """
    An entity designed to apply module effects to other machines in its radius.
    """

    @property
    def similar_entities(self) -> list[str]:
        return beacons

    # =========================================================================

    __hash__ = Entity.__hash__
