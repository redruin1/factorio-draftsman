# storage_tank.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections
from draftsman.utils import get_first
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import storage_tanks

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class StorageTank(CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    An entity that stores a fluid.
    """

    class Format(
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="StorageTank")

    def __init__(
        self,
        name: Optional[str] = get_first(storage_tanks),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        connections: Connections = {},
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
            storage_tanks,
            position=position,
            tile_position=tile_position,
            direction=direction,
            connections=connections,
            tags=tags,
            **kwargs,
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    __hash__ = Entity.__hash__
