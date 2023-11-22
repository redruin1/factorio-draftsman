# filter_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel, FilterEntry, uint8

from draftsman.data.entities import filter_inserters

from pydantic import ConfigDict, Field, field_validator
from typing import Any, Literal, Optional, Union


class FilterInserter(
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that can move items between machines, and has the ability to only
    move specific items.

    .. NOTE::

        In Factorio, the ``Inserter`` prototype includes both regular and filter
        inserters. In Draftsman, inserters are split into two different classes,
        :py:class:`~.Inserter` and :py:class:`~.FilterInserter`. This might
        change in a future version of Draftsman.
    """

    class Format(
        FiltersMixin.Format,
        StackSizeMixin.Format,
        CircuitReadHandMixin.Format,
        InserterModeOfOperationMixin.Format,
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        EnableDisableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            StackSizeMixin.ControlFormat,
            CircuitReadHandMixin.ControlFormat,
            InserterModeOfOperationMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            EnableDisableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        filter_mode: Optional[Literal["whitelist", "blacklist"]] = Field(
            "whitelist",
            description="""
            Whether or not to treat the item filters associated with this 
            inserter as a list of items to allow or a list of items to disallow.
            """,
        )

        # @field_validator("filters", mode="before")
        # @classmethod
        # def handle_filter_shorthand(cls, value: Any):
        #     print("input:", value)
        #     if isinstance(value, (list, tuple)):
        #         result = []
        #         for i, entry in enumerate(value):
        #             if isinstance(entry, str):
        #                 result.append({"index": i + 1, "name": entry})
        #             else:
        #                 result.append(entry)
        #         print("result:", result)
        #         return result
        #     else:
        #         return value

        model_config = ConfigDict(title="FilterInserter")

    def __init__(
        self,
        name: str = filter_inserters[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        override_stack_size: uint8 = None,
        filters: list[FilterEntry] = [],
        filter_mode: Literal["whitelist", "blacklist"] = "whitelist",
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format

        super().__init__(
            name,
            filter_inserters,
            position=position,
            tile_position=tile_position,
            direction=direction,
            override_stack_size=override_stack_size,
            filters=filters,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.filter_mode = filter_mode

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def filter_mode(self) -> Literal["whitelist", "blacklist", None]:
        """
        The mode that the filter is set to. Can be either ``"whitelist"`` or
        ``"blacklist"``.

        :getter: Gets the filter mode.
        :setter: Sets the filter mode.
        :type: ``str``

        :exception ValueError: If set to a ``str`` that is neither ``"whitelist"``
            nor ``"blacklist"``.
        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return self._root.filter_mode

    @filter_mode.setter
    def filter_mode(self, value: Literal["whitelist", "blacklist", None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "filter_mode", value
            )
            self._root.filter_mode = result
        else:
            self._root.filter_mode = value

    # =========================================================================

    def merge(self, other: "FilterInserter"):
        super().merge(other)

        self.filter_mode = other.filter_mode

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filter_mode == other.filter_mode
