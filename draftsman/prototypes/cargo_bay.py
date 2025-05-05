# cargo_bay.py

from draftsman.classes.entity import Entity

# from draftsman.classes.mixins import ()
from draftsman.constants import ValidationMode
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.utils import get_first

from draftsman.data.entities import cargo_bays

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class CargoBay(Entity):
    """
    An entity which can be added to a CargoLandingPad or a SpacePlatformHub in
    order to expand its inventory size and the amount of cargo pods it can
    send/recieve.
    """

    @property
    def similar_entities(self) -> list[str]:
        return cargo_bays

    # =========================================================================

    __hash__ = Entity.__hash__
