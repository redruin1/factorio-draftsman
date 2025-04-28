# radar.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, EnergySourceMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import radars

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class Radar(CircuitConnectableMixin, EnergySourceMixin, Entity):
    """
    An entity that scans neighbouring chunks periodically.
    """

    # class Format(CircuitConnectableMixin.Format, Entity.Format):
    #     model_config = ConfigDict(title="Radar")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(radars),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         radars,
    #         position=position,
    #         tile_position=tile_position,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return radars

    # =========================================================================

    __hash__ = Entity.__hash__
