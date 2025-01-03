# solar_panel.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import solar_panels

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class SolarPanel(Entity):
    """
    An entity that produces electricity depending on the presence of the sun.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="SolarPanel")

    def __init__(
        self,
        name: Optional[str] = get_first(solar_panels),
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
            solar_panels,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
