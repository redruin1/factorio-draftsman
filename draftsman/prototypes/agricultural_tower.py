# agricultural_tower.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

from draftsman.data.entities import agricultural_towers

import attrs


@attrs.define
class AgriculturalTower(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that can plant and harvest growables.
    """

    # class Format(
    #     CircuitConditionMixin.Format,
    #     LogisticConditionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CircuitConditionMixin.ControlFormat,
    #         LogisticConditionMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         read_contents: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to broadcast the current inventory of the tower
    #             to any connected circuit network.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="AgriculturalTower")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(agricultural_towers),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     override_stack_size: uint8 = None,
    #     control_behavior: Format.ControlBehavior = {},
    #     items: dict[str, uint32] = {},  # TODO: ItemID
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         agricultural_towers,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         override_stack_size=override_stack_size,
    #         control_behavior=control_behavior,
    #         items=items,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return agricultural_towers

    # =========================================================================

    read_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to broadcast the entities inside of this tower's inventory to
    any connected circuit network.
    """

    # @property
    # def read_contents(self) -> Optional[bool]:
    #     """
    #     Whether or not this Entity is set to output it's contents to a
    #     connected circuit network.

    #     :getter: Gets the value of ``read_contents``, or ``None`` if not set.
    #     :setter: Sets the value of ``read_contents``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.read_contents

    # @read_contents.setter
    # def read_contents(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_contents",
    #             value,
    #         )
    #         self.control_behavior.read_contents = result
    #     else:
    #         self.control_behavior.read_contents = value

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:entity:agricultural_tower"},
    AgriculturalTower,
    lambda fields: {("control_behavior", "read_contents"): fields.read_contents.name},
)
