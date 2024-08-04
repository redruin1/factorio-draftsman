# player_port.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import player_ports

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class PlayerPort(Entity):
    """
    A constructable respawn point typically used in scenarios.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="PlayerPort")

    def __init__(
        self,
        name: Optional[str] = get_first(player_ports),
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
            name,
            player_ports,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment
