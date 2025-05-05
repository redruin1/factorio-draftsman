# inserter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import inserters

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class Inserter(
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity with a swinging arm that can move items between machines.
    """

    # class Format(
    #     FiltersMixin.Format,
    #     StackSizeMixin.Format,
    #     CircuitReadHandMixin.Format,
    #     InserterModeOfOperationMixin.Format,
    #     CircuitConditionMixin.Format,
    #     LogisticConditionMixin.Format,
    #     CircuitEnableMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         StackSizeMixin.ControlFormat,
    #         CircuitReadHandMixin.ControlFormat,
    #         InserterModeOfOperationMixin.ControlFormat,
    #         CircuitConditionMixin.ControlFormat,
    #         LogisticConditionMixin.ControlFormat,
    #         CircuitEnableMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         circuit_set_filters: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not inputs from the circuit network should determine
    #             item filters.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     pickup_position: Optional[list[float]] = Field(
    #         None,
    #         description="""
    #         The pickup position to use. Not configurable in vanilla, but
    #         settable via script or mods.
    #         """,
    #     )
    #     drop_position: Optional[list[float]] = Field(
    #         None,
    #         description="""
    #         The drop position to use. Not configurable in vanilla, but settable
    #         via script or mods.
    #         """,
    #     )
    #     filter_mode: Optional[Literal["whitelist", "blacklist"]] = Field(
    #         "whitelist",
    #         description="""
    #         Whether or not to treat the item filters associated with this
    #         inserter as a list of items to allow or a list of items to disallow.
    #         """,
    #     )
    #     spoil_priority: Optional[Literal["spoiled-first", "fresh-first"]] = Field(
    #         None,
    #         description="""
    #         Whether to prefer grabbing the most spoiled or most fresh items from
    #         an inventory.
    #         """,
    #     )

    #     model_config = ConfigDict(title="Inserter")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(inserters),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     pickup_position: Optional[list[float]] = None,
    #     drop_position: Optional[list[float]] = None,
    #     filter_mode: Literal["whitelist", "blacklist"] = "whitelist",
    #     spoil_priority: Literal["spoiled-first", "fresh-first", None] = None,
    #     override_stack_size: uint8 = None,
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         inserters,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         override_stack_size=override_stack_size,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.pickup_position = pickup_position  # TODO: defaults
    #     self.drop_position = drop_position  # TODO: defaults

    #     self.filter_mode = filter_mode

    #     self.spoil_priority = spoil_priority

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return inserters

    # =========================================================================

    pickup_position: Optional[list[float]] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    The pickup position of the inserter.

    TODO
    """

    # @property
    # def pickup_position(self) -> Optional[list[float]]:
    #     """
    #     The pickup position of the inserter.

    #     TODO
    #     """
    #     return self._root.pickup_position

    # @pickup_position.setter
    # def pickup_position(self, value: Optional[list[float]]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "pickup_position",
    #             value,
    #         )
    #         self._root.pickup_position = result
    #     else:
    #         self._root.pickup_position = value

    # =========================================================================

    drop_position: Optional[list[float]] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    The drop position of the inserter.

    TODO
    """

    # @property
    # def drop_position(self) -> Optional[list[float]]:
    #     """
    #     The drop position of the inserter.

    #     TODO
    #     """
    #     return self._root.drop_position

    # @drop_position.setter
    # def drop_position(self, value: Optional[list[float]]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "drop_position",
    #             value,
    #         )
    #         self._root.drop_position = result
    #     else:
    #         self._root.drop_position = value

    # =========================================================================

    filter_mode: Literal["whitelist", "blacklist"] = attrs.field(
        default="whitelist", validator=one_of("whitelist", "blacklist")
    )
    """
    The mode that the given filter should operate under. 

    :exception DataFormatError: If set to a value that is neither ``"whitelist"``
        nor ``"blacklist"``.
    """

    # @property
    # def filter_mode(self) -> Literal["whitelist", "blacklist", None]:
    #     """
    #     The mode that the filter is set to. Can be either ``"whitelist"`` or
    #     ``"blacklist"``.

    #     :getter: Gets the filter mode.
    #     :setter: Sets the filter mode.

    #     :exception ValueError: If set to a ``str`` that is neither ``"whitelist"``
    #         nor ``"blacklist"``.
    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     """
    #     return self._root.filter_mode

    # @filter_mode.setter
    # def filter_mode(self, value: Literal["whitelist", "blacklist", None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "filter_mode", value
    #         )
    #         self._root.filter_mode = result
    #     else:
    #         self._root.filter_mode = value

    # =========================================================================

    spoil_priority: Literal["spoiled-first", "fresh-first", None] = attrs.field(
        default=None,  # TODO: is this true?
        validator=one_of("spoiled-first", "fresh-first", None),
    )
    """
    Whether or not this inserter should prefer most fresh or most spoiled
    items when grabbing from an inventory. If set to ``None``, this inserter
    will ignore the spoiled value of items entirely.

    :raises DataFormatError: When set to a value other than ``"spoiled-first"``,
        ``"fresh-first"``, or ``None``.
    """

    # @property
    # def spoil_priority(self) -> Literal["spoiled-first", "fresh-first", None]:
    #     """
    #     Whether or not this inserter should prefer most fresh or most spoiled
    #     items when grabbing from an inventory.

    #     TODO
    #     """
    #     return self._root.spoil_priority

    # @spoil_priority.setter
    # def spoil_priority(
    #     self, value: Literal["spoiled-first", "fresh-first", None]
    # ) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "spoil_priority", value
    #         )
    #         self._root.spoil_priority = result
    #     else:
    #         self._root.spoil_priority = value

    # =========================================================================

    # circuit_set_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    # """
    # Whether or not the inserter should have its filters determined via
    # signals on connected circuit networks.

    # :raises DataFormatError: If set to anything other than a ``bool``.
    # """

    # @property
    # def circuit_set_filters(self) -> Optional[bool]:
    #     """
    #     Whether or not the inserter should have its filters determined via
    #     signals on connected circuit networks.

    #     TODO
    #     """
    #     return self.control_behavior.circuit_set_filters

    # @circuit_set_filters.setter
    # def circuit_set_filters(
    #     self, value: Literal["spoiled-first", "fresh-first", None]
    # ) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_set_filters",
    #             value,
    #         )
    #         self.control_behavior.circuit_set_filters = result
    #     else:
    #         self.control_behavior.circuit_set_filters = value

    # =========================================================================

    def merge(self, other: "Inserter"):
        super().merge(other)

        self.circuit_set_filters = other.circuit_set_filters
        self.pickup_position = other.pickup_position
        self.drop_position = other.drop_position
        self.filter_mode = other.filter_mode
        self.spoil_priority = other.spoil_priority

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_schema(  # pragma: no branch
    {
        "$id": "factorio:inserter",
    },
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position.name,
        "drop_position": fields.drop_position.name,
        "filter_mode": fields.filter_mode.name,
        None: fields.spoil_priority.name,
    },
)


draftsman_converters.get_version((2, 0)).add_schema(
    {
        "$id": "factorio:inserter",
    },
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position.name,
        "drop_position": fields.drop_position.name,
        "filter_mode": fields.filter_mode.name,
        "spoil_priority": fields.spoil_priority.name,
    },
)
