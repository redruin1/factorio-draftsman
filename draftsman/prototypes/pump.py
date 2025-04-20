# pump.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.signatures import DraftsmanBaseModel
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import pumps

import attrs
from pydantic import ConfigDict
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class Pump(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that aids fluid transfer through pipes.

    :param name: The name of this entity.
    :param id: A user-given identifier for easy accessing.
    :param quality: The quality of the entity.
    :param position: The position of the entity.
    :param tile_position: The tile position of the entity.
    :param tags: Additional keys, usually populated by mods.
    :param direction: The orientation of the entity.
    :param circuit_condition: The circuit condition that this entity needs to 
        satisfy in order to operate.
    :param connect_to_logistic_network: Whether or not this entity should use
        the neighbouring logistic network to influence its behavior.
    :param logistic_condition: The logistic condition that this entity needs to
        satisfy in order to operate.
    :param validate_assignment: Whether or not to validate attribute assignment
        for this entity, either during or after construction.
    :param extra_keys: Any additional dictionary keys/values that are not valid
        under this entity's schema. Unknown keys on import will be collected
        here, and if there are any values 
    """

    # class Format(
    #     CircuitConditionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(CircuitConditionMixin.ControlFormat, DraftsmanBaseModel):
    #         pass

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="SimpleEntityWithOwner")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(pumps),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         pumps,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return pumps

    # =========================================================================

    __hash__ = Entity.__hash__
