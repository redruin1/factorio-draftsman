# rail_signal.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import rail_signals

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class RailSignal(
    ReadRailSignalMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
    Entity,
):
    """
    A rail signal that determines whether or not trains can pass along their
    rail block.
    """

    class Format(
        ReadRailSignalMixin.Format,
        CircuitConditionMixin.Format,
        CircuitEnableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        EightWayDirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            ReadRailSignalMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            CircuitEnableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            circuit_close_signal: Optional[bool] = Field(
                False,
                description="""
                Whether or not to have this signal close off if a circuit 
                condition is met. 'enable_disable' equivalent for train signals.
                """,
            )
            circuit_read_signal: Optional[bool] = Field(
                True,
                description="""
                Whether or not to output the state of this train signal to any
                connected circuit network.
                """,
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="RailSignal")

    def __init__(
        self,
        name: Optional[str] = get_first(rail_signals),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self.control_behavior: __class__.Format.ControlBehavior

        # Set a (private) flag to indicate to the constructor to not generate
        # rotations, and rather just use the same collision set regardless of
        # rotation
        self._disable_collision_set_rotation = True

        super().__init__(
            name,
            rail_signals,
            position=position,
            tile_position=tile_position,
            direction=direction,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def enable_disable(self) -> Optional[bool]:
        return self.control_behavior.circuit_close_signal

    @enable_disable.setter
    def enable_disable(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_close_signal",
                value,
            )
            self.control_behavior.circuit_close_signal = result
        else:
            self.control_behavior.circuit_close_signal = value

    # =========================================================================

    @property
    def read_signal(self) -> Optional[bool]:
        """
        Whether or not to read the state of the rail signal as their output
        signals.

        :getter: Gets whether or not to read the signal, or ``None`` if not set.
        :setter: Sets whether or not to read the signal. Removes the key if set
            to ``None``.

        :exception DataFormatError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_signal

    @read_signal.setter
    def read_signal(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_read_signal",
                value,
            )
            self.control_behavior.circuit_read_signal = result
        else:
            self.control_behavior.circuit_read_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__
