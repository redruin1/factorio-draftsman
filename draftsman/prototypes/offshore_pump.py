# offshore_pump.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import offshore_pumps

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class OffshorePump(
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that pumps a fluid from the environment.
    """

    # class Format(
    #     CircuitConditionMixin.Format,
    #     LogisticConditionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CircuitConditionMixin.ControlFormat,
    #         LogisticConditionMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         pass

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="OffshorePump")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(offshore_pumps),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """
    #     self._root: __class__.Format
    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         offshore_pumps,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return offshore_pumps

    # =========================================================================

    __hash__ = Entity.__hash__
