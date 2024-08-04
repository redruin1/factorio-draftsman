# container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    CircuitConnectableMixin,
    InventoryMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import Connections, uint16, uint32
from draftsman.utils import get_first

from draftsman.data.entities import containers

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Container(InventoryMixin, RequestItemsMixin, CircuitConnectableMixin, Entity):
    """
    An entity that holds items.
    """

    class Format(
        InventoryMixin.Format,
        RequestItemsMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="Container")

    def __init__(
        self,
        name: Optional[str] = get_first(containers),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        items: dict[str, uint32] = {},  # TODO: ItemID
        connections: Connections = {},
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
            name,
            containers,
            position=position,
            tile_position=tile_position,
            bar=bar,
            items=items,
            connections=connections,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
