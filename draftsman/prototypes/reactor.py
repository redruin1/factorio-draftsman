# reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import AttrsSignalID
from draftsman.utils import get_first
from draftsman.validators import instance_of

from draftsman.data.entities import reactors

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class Reactor(
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that converts a fuel into thermal energy.
    """

    # TODO: technically, a reactor can have more than just a burnable energy
    # source; it could have any type of energy source other than heat as
    # input. Thus, we need to make sure that the attributes from
    # BurnerEnergySourceMixin are only used in the correct configuration

    # class Format(
    #     BurnerEnergySourceMixin.Format,
    #     ItemRequestMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         read_burner_fuel: Optional[bool] = Field(
    #             False,
    #             description="""Whether or not to broadcast the amount of fuel currently in the reactor to any connected circuit networks..""",
    #         )
    #         read_temperature: Optional[bool] = Field(
    #             False,
    #             description="""Whether or not to brodcast the current temperature in Celsius of the reactor to any connected circuit networks.""",
    #         )
    #         temperature_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-T", type="virtual"),
    #             description="""What signal to broadcast the reactors temperature on, if "read_temperature" is true.""",
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="Reactor")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(reactors),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     items: Optional[list[ItemRequest]] = [],
    #     control_behavior: Optional[Format.ControlBehavior] = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         reactors,
    #         position=position,
    #         tile_position=tile_position,
    #         items=items,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return reactors

    # =========================================================================

    read_burner_fuel: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to broadcast the amount of fuel currently in the reactor to 
    any connected circuit networks.
    """

    # @property
    # def read_burner_fuel(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.read_burner_fuel

    # @read_burner_fuel.setter
    # def read_burner_fuel(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_burner_fuel",
    #             value,
    #         )
    #         self.control_behavior.read_burner_fuel = result
    #     else:
    #         self.control_behavior.read_burner_fuel = value

    # =========================================================================

    read_temperature: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    Whether or not to brodcast the current temperature in Celsius of the reactor 
    to any connected circuit networks.
    """

    # @property
    # def read_temperature(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.read_temperature

    # @read_temperature.setter
    # def read_temperature(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_temperature",
    #             value,
    #         )
    #         self.control_behavior.read_temperature = result
    #     else:
    #         self.control_behavior.read_temperature = value

    # =========================================================================

    temperature_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-T", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal with which to broadcast the reactors temperature to, if this 
    entity is configured to do so.
    """

    # @property
    # def temperature_signal(self) -> Optional[SignalID]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.temperature_signal

    # @temperature_signal.setter
    # def temperature_signal(self, value: Optional[SignalID]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "temperature_signal",
    #             value,
    #         )
    #         self.control_behavior.temperature_signal = result
    #     else:
    #         self.control_behavior.temperature_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__
