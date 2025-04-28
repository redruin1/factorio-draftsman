# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    RequestItemsMixin,
    EnergySourceMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import ItemRequest
from draftsman.utils import get_first

from draftsman.data.entities import beacons

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class Beacon(ModulesMixin, RequestItemsMixin, EnergySourceMixin, Entity):
    """
    An entity designed to apply module effects to other machines in its radius.
    """

    # class Format(
    #     ModulesMixin.Format,
    #     RequestItemsMixin.Format,
    #     Entity.Format,
    # ):
    #     model_config = ConfigDict(title="Beacon")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(beacons),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     items: Optional[list[ItemRequest]] = [],
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         beacons,
    #         position=position,
    #         tile_position=tile_position,
    #         items=items,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return beacons

    # =========================================================================

    __hash__ = Entity.__hash__
