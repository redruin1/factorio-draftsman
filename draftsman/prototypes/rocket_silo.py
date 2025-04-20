# rocket_silo.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    ModulesMixin,
    RequestItemsMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
)
from draftsman.constants import SiloReadMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import DraftsmanBaseModel, RecipeName, uint32
from draftsman.validators import enum_converter, instance_of

from draftsman.data.entities import rocket_silos

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class RocketSilo(
    ModulesMixin,
    RequestItemsMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    Entity,
):
    """
    An entity that produces rockets, usually used in research.
    """

    class Format(
        ModulesMixin.Format,
        RequestItemsMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        RecipeMixin.Format,
        Entity.Format,
    ):
        # auto_launch: Optional[bool] = Field(
        #     False,
        #     description="""
        #     Whether or not this silo is configured to automatically launch
        #     itself when cargo is present inside of it.
        #     """,
        # )

        class ControlBehavior(DraftsmanBaseModel):
            read_items_mode: Optional[SiloReadMode] = SiloReadMode.READ_CONTENTS

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        transitional_request_index: Optional[uint32] = Field(  # TODO: size, wtf is this
            0, description="""TODO"""
        )

        model_config = ConfigDict(title="RocketSilo")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(rocket_silos),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     recipe: Optional[str] = "rocket-part",
    #     recipe_quality: Optional[
    #         Literal["normal", "uncommon", "rare", "epic", "legendary"]
    #     ] = "normal",
    #     # auto_launch: bool = False,
    #     transitional_request_index: Optional[uint32] = 0,
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

    #     self._root: __class__.Format
    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         rocket_silos,
    #         position=position,
    #         tile_position=tile_position,
    #         recipe=recipe,
    #         recipe_quality=recipe_quality,
    #         items=items,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     # self.auto_launch = auto_launch
    #     self.transitional_request_index = transitional_request_index

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return rocket_silos

    # =========================================================================

    # TODO: we should just "evolve" the attribute instead of redefining it
    # See https://github.com/python-attrs/attrs/issues/637
    # recipe: Optional[RecipeName] = attrs.field(
    #     default="rocket-part",
    #     validator=instance_of(Optional[RecipeName])
    # )

    # =========================================================================

    auto_launch: Optional[bool] = attrs.field(
        default=False,
        validator=instance_of(Optional[bool])
    )
    """
    Whether or not to automatically launch the rocket when it's cargo is
    full. Deprecated in Factorio 2.0.
    """

    # @property
    # def auto_launch(self) -> Optional[bool]:
    #     """
    #     Whether or not to automatically launch the rocket when it's cargo is
    #     full. Deprecated in Factorio 2.0.

    #     :getter: Gets whether or not to automatically launch.
    #     :setter: Sets whether or not to automatically launch.

    #     :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    #     """
    #     return self._root.auto_launch

    # @auto_launch.setter
    # def auto_launch(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "auto_launch", value
    #         )
    #         self._root.auto_launch = result
    #     else:
    #         self._root.auto_launch = value

    # =========================================================================

    read_items_mode: SiloReadMode = attrs.field(
        default=SiloReadMode.NONE,
        converter=enum_converter(SiloReadMode),
        validator=instance_of(SiloReadMode),
    )
    """
    TODO
    """

    # @property
    # def read_items_mode(self) -> Optional[SiloReadMode]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.read_items_mode

    # @read_items_mode.setter
    # def read_items_mode(self, value: Optional[SiloReadMode]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_items_mode",
    #             value,
    #         )
    #         self.control_behavior.read_items_mode = result
    #     else:
    #         self.control_behavior.read_items_mode = value

    # =========================================================================

    transitional_request_index: uint32 = attrs.field(
        default=0,
        validator=instance_of(uint32)
    )
    """
    TODO
    """

    # @property
    # def transitional_request_index(self) -> Optional[uint32]:
    #     """
    #     TODO
    #     """
    #     return self._root.transitional_request_index

    # @transitional_request_index.setter
    # def transitional_request_index(self, value: Optional[uint32]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "transitional_request_index", value
    #         )
    #         self._root.transitional_request_index = result
    #     else:
    #         self._root.transitional_request_index = value

    # =========================================================================

    def merge(self, other: "RocketSilo"):
        super(RocketSilo, self).merge(other)

        self.auto_launch = other.auto_launch
        self.read_items_mode = other.read_items_mode
        self.transitional_request_index = other.transitional_request_index

    # =========================================================================

    __hash__ = Entity.__hash__

    # def __eq__(self, other: "RocketSilo") -> bool:
    #     return (
    #         super().__eq__(other)
    #         # and self.auto_launch == other.auto_launch
    #         and self.transitional_request_index == other.transitional_request_index
    #     )


draftsman_converters.get_version((1, 0)).add_schema(
    {
        "$id": "factorio:rocket_silo_v1.0"
    },
    RocketSilo,
    lambda fields: {
        fields.auto_launch.name: "auto_launch",
        fields.read_items_mode: None,
        fields.transitional_request_index: None,
    }
)

draftsman_converters.get_version((2, 0)).add_schema(
    {
        "$id": "factorio:rocket_silo_v2.0"
    },
    RocketSilo,
    lambda fields: {
        fields.auto_launch.name: None,
        fields.read_items_mode.name: ("control_behavior", "read_items_mode"),
        fields.transitional_request_index.name: "transitional_request_index",
    }
)