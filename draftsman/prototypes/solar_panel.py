# solar_panel.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode

from draftsman.data.entities import solar_panels

from pydantic import ConfigDict
from typing import Any, Literal, Union


class SolarPanel(Entity):
    """
    An entity that produces electricity depending on the presence of the sun.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="SolarPanel")

    def __init__(
        self,
        name: str = solar_panels[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
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
            solar_panels,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    __hash__ = Entity.__hash__
