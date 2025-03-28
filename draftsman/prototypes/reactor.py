# reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    BurnerEnergySourceMixin,
    RequestItemsMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import DraftsmanBaseModel, ItemRequest, SignalID
from draftsman.utils import get_first

from draftsman.data.entities import reactors

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Reactor(
    BurnerEnergySourceMixin,
    RequestItemsMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    An entity that converts a fuel into thermal energy.
    """

    class Format(
        BurnerEnergySourceMixin.Format,
        RequestItemsMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(DraftsmanBaseModel):
            read_burner_fuel: Optional[bool] = Field(
                False,
                description="""Whether or not to broadcast the amount of fuel currently in the reactor to any connected circuit networks..""",
            )
            read_temperature: Optional[bool] = Field(
                False,
                description="""Whether or not to brodcast the current temperature in Celsius of the reactor to any connected circuit networks.""",
            )
            temperature_signal: Optional[SignalID] = Field(
                SignalID(name="signal-T", type="virtual"),
                description="""What signal to broadcast the reactors temperature on, if "read_temperature" is true.""",
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="Reactor")

    def __init__(
        self,
        name: Optional[str] = get_first(reactors),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        items: Optional[list[ItemRequest]] = [],
        control_behavior: Optional[Format.ControlBehavior] = {},
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
            reactors,
            position=position,
            tile_position=tile_position,
            items=items,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        # TODO: technically, a reactor can have more than just a burnable energy
        # source; it could have any type of energy source other than heat as
        # input. Thus, we need to make sure that the attributes from
        # BurnerEnergySourceMixin are only used in the correct configuration

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def allowed_items(self) -> Optional[set[str]]:
        return self.allowed_fuel_items

    # =========================================================================

    @property
    def read_burner_fuel(self) -> Optional[bool]:
        """
        TODO
        """
        return self.control_behavior.read_burner_fuel

    @read_burner_fuel.setter
    def read_burner_fuel(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_burner_fuel",
                value,
            )
            self.control_behavior.read_burner_fuel = result
        else:
            self.control_behavior.read_burner_fuel = value

    # =========================================================================

    @property
    def read_temperature(self) -> Optional[bool]:
        """
        TODO
        """
        return self.control_behavior.read_temperature

    @read_temperature.setter
    def read_temperature(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_temperature",
                value,
            )
            self.control_behavior.read_temperature = result
        else:
            self.control_behavior.read_temperature = value

    # =========================================================================

    @property
    def temperature_signal(self) -> Optional[SignalID]:
        """
        TODO
        """
        return self.control_behavior.temperature_signal

    @temperature_signal.setter
    def temperature_signal(self, value: Optional[SignalID]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "temperature_signal",
                value,
            )
            self.control_behavior.temperature_signal = result
        else:
            self.control_behavior.temperature_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__
