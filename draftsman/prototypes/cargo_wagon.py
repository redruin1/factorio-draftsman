# cargo_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    InventoryFilterMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import InventoryFilters, uint32
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import cargo_wagons
from draftsman.data import entities

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class CargoWagon(RequestItemsMixin, InventoryFilterMixin, OrientationMixin, Entity):
    """
    A train wagon that holds items as cargo.
    """

    class Format(
        RequestItemsMixin.Format,
        InventoryFilterMixin.Format,
        OrientationMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="CargoWagon")

    def __init__(
        self,
        name: str = cargo_wagons[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Orientation = Orientation.NORTH,
        items: dict[str, uint32] = {},  # TODO: ItemID
        inventory: InventoryFilters = InventoryFilters(),
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        super().__init__(
            name,
            cargo_wagons,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            items=items,
            inventory=inventory,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        if validate:
            self.validate(mode=validate).reissue_all(stacklevel=3)

    # TODO: check for item requests exceeding cargo capacity

    # =========================================================================

    __hash__ = Entity.__hash__
