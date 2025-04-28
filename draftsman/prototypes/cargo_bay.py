# cargo_bay.py

from draftsman.classes.entity import Entity

# from draftsman.classes.mixins import ()
from draftsman.constants import ValidationMode
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.utils import get_first

from draftsman.data.entities import cargo_bays

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class CargoBay:
    """
    An entity which can be added to a CargoLandingPad or a SpacePlatformHub in
    order to expand its inventory size and the amount of cargo pods it can
    send/recieve.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="CargoBay")

    # TODO: validation to ensure that cargo bays are connected to their hubs

    def __init__(
        self,
        name: Optional[str] = get_first(cargo_bays),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name=name,
            similar_entities=cargo_bays,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return cargo_bays

    # =========================================================================

    __hash__ = Entity.__hash__
