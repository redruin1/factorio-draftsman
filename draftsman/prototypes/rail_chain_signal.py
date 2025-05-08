# rail_chain_signal.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    # EightWayDirectionalMixin,
    DirectionalMixin
)
from draftsman.constants import Direction, SIXTEEN_WAY_DIRECTIONS
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import rail_chain_signals

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class RailChainSignal(
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    # EightWayDirectionalMixin,
    DirectionalMixin,
    Entity,
):
    """
    A rail signal that determines access of a current rail block based on a
    forward rail block.
    """

    # TODO: does this entity have rail signal control via circuit network? If so
    # abstract the code from RailSignal out and use it in both

    # class Format(
    #     ReadRailSignalMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     EightWayDirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(ReadRailSignalMixin.ControlFormat, DraftsmanBaseModel):
    #         blue_output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-blue", type="virtual"),
    #             description="""
    #             Circuit signal to output when the train signal reads blue.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="RailChainSignal")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(rail_chain_signals),
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

    #     self.control_behavior: __class__.Format.ControlBehavior

    #     # Set a (private) flag to indicate to the constructor to not generate
    #     # rotations, and rather just use the same collision set regardless of
    #     # rotation
    #     self._disable_collision_set_rotation = True

    #     super().__init__(
    #         name,
    #         rail_chain_signals,
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
        return rail_chain_signals
    

    # =========================================================================

    @property
    def collision_set_rotated(self) -> bool:
        return False

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return SIXTEEN_WAY_DIRECTIONS
    
    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        # This entity doesn't actually rotate it's collision box
        return self.static_collision_set

    # =========================================================================

    blue_output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-blue", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The blue output signal. Sent with a unit value when the rail signal's state 
    is blue.
    """

    # @property
    # def blue_output_signal(self) -> Optional[SignalID]:
    #     """
    #     The blue output signal. Sent when the rail signal's state is blue.

    #     Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
    #     ``name`` is the name of the signal and ``type`` is it's type, either
    #     ``"item"``, ``"fluid"``, or ``"signal"``.

    #     However, because a signal's type is always constant and can be inferred,
    #     it is recommended to simply set the attribute to the string name of the
    #     signal which will automatically be converted to the above format.

    #     :getter: Gets the blue output signal, or ``None`` if not set.
    #     :setter: Sets the blue output signal. Removes the key if set to ``None``.

    #     :exception InvalidSignalID: If set to a string that is not a valid
    #         signal name.
    #     :exception DataFormatError: If set to a dict that does not match the
    #         dict format specified above.
    #     """
    #     return self.control_behavior.blue_output_signal

    # @blue_output_signal.setter
    # def blue_output_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "blue_output_signal",
    #             value,
    #         )
    #         self.control_behavior.blue_output_signal = result
    #     else:
    #         self.control_behavior.blue_output_signal = value

    # =========================================================================

    def merge(self, other: "RailChainSignal"):
        super().merge(other)

        self.blue_output_signal = other.blue_output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:rail_chain_signal"},
    RailChainSignal,
    lambda fields: {
        ("control_behavior", "blue_output_signal"): fields.blue_output_signal.name
    },
)
