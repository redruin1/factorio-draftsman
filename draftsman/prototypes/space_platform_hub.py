# space_platform_hub.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    RequestFiltersMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import DraftsmanBaseModel, SignalID
from draftsman.utils import get_first

from draftsman.data.entities import space_platform_hubs

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class SpacePlatformHub(
    RequestFiltersMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
):
    """
    Main control center of space platforms.
    """

    class Format(
        RequestFiltersMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(DraftsmanBaseModel):
            read_contents: Optional[bool] = Field(
                True,
                description="""Broadcast the inventory contents of the hub to the connected circuit networks.""",
            )
            send_to_platform: Optional[bool] = Field(
                True,
                description="""Whether or not to send the contents of the circuit network to the platform for determining it's circuit conditions.""",
            )
            read_moving_from: Optional[bool] = Field(
                False,
                description="""Whether or not to send the planet the platform is currently moving from to the circuit network.""",
            )
            read_moving_to: Optional[bool] = Field(
                False,
                description="""Whether or not to send the planet the platform is currently moving to to the circuit network.""",
            )
            read_speed: Optional[bool] = Field(
                False,
                description="""Whether or not to send the current speed of the space platform to the circuit network.""",
            )
            speed_signal: Optional[SignalID] = Field(
                SignalID(name="signal-V", type="virtual"),
                description="""The signal to broadcast the platforms current speed on.""",
            )
            read_damage_taken: Optional[bool] = Field(
                False,
                description="""Whether or not to send the cumulative damage taken on this leg of the trip to the circuit network.""",
            )
            damage_taken_signal: Optional[SignalID] = Field(
                SignalID(name="signal-D", type="virtual"),
                description="""The signal to broadcast the damage taken by the platform on.""",
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        request_missing_construction_materials: Optional[bool] = Field(
            True,
            description="""Whether or not to automatically request construction materials from configured surfaces the platform lies above.""",
        )

        model_config = ConfigDict(title="SpacePlatformHub")

    def __init__(
        self,
        name: Optional[str] = get_first(space_platform_hubs),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        control_behavior: Optional[Format.ControlBehavior] = {},
        request_missing_construction_materials: Optional[bool] = True,
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """
        self._root: self.Format

        super().__init__(
            name=name,
            similar_entities=space_platform_hubs,
            position=position,
            tile_position=tile_position,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.request_missing_construction_materials = (
            request_missing_construction_materials
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def request_missing_construction_materials(self) -> Optional[bool]:
        """
        TODO
        """
        return self._root.request_missing_construction_materials

    @request_missing_construction_materials.setter
    def request_missing_construction_materials(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "request_missing_construction_materials",
                value,
            )
            self._root.request_missing_construction_materials = result
        else:
            self._root.request_missing_construction_materials = value

    @property
    def similar_entities(self) -> list[str]:
        return space_platform_hubs

    # =========================================================================

    __hash__ = Entity.__hash__
