# power_switch.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
    # DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.data import entities
from draftsman.signatures import Connections, DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import power_switches

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class PowerSwitch(
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
    # DirectionalMixin,
    Entity,
):
    """
    An entity that connects or disconnects a power network.
    """

    class Format(
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        PowerConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        switch_state: Optional[bool] = Field(
            False,
            description="""
            The manual override state for this switch, where false is off and
            true is on. Superceeded by any circuit or logistic condition.
            """,
        )

        model_config = ConfigDict(title="PowerSwitch")

    def __init__(
        self,
        name: Optional[str] = get_first(power_switches),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        switch_state: bool = False,
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        super().__init__(
            name,
            power_switches,
            position=position,
            tile_position=tile_position,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.switch_state = switch_state

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def dual_power_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def maximum_wire_distance(self) -> float:
        # Power switches use a custom key (for some reason)
        return entities.raw.get(self.name, {"wire_max_distance": None}).get(
            "wire_max_distance", 0
        )

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        # Power switches use a custom key (for some reason)
        return entities.raw.get(self.name, {"wire_max_distance": None}).get(
            "wire_max_distance", 0
        )

    # =========================================================================

    @property
    def switch_state(self) -> Optional[bool]:
        """
        Whether the switch is passing electricity or not. This is a manual
        setting that is overridden by the circuit or logistic condition.

        :getter: Gets the value of the switch state.
        :setter: Sets the value of the switch state.

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._root.get("switch_state", None)

    @switch_state.setter
    def switch_state(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "switch_state", value
            )
            self._root["switch_state"] = result
        else:
            self._root["switch_state"] = value

    # =========================================================================

    def merge(self, other: "PowerSwitch") -> None:
        super().merge(other)

        self.switch_state = other.switch_state

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.switch_state == other.switch_state
