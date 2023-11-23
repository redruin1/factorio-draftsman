# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    RequestItemsMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint32

from draftsman.data.entities import beacons

from pydantic import ConfigDict
from typing import Any, Literal, Union


class Beacon(InputIngredientsMixin, ModulesMixin, RequestItemsMixin, Entity):
    """
    An entity designed to apply module effects to other machine's in it's radius.
    """

    class Format(
        InputIngredientsMixin.Format,
        ModulesMixin.Format,
        RequestItemsMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="Beacon")

    def __init__(
        self,
        name: str = beacons[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name,
            beacons,
            position=position,
            tile_position=tile_position,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def allowed_input_ingredients(self) -> set[str]:
        """
        Gets the list of items that are valid inputs ingredients for crafting
        machines of all types. Returns ``None`` if this entity's name is not
        recognized by Draftsman. Not exported; read only.
        """
        return set()

    # =========================================================================

    __hash__ = Entity.__hash__
