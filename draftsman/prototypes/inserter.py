# inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
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
from draftsman.signatures import Connections, DraftsmanBaseModel, uint8

from draftsman.data.entities import inserters

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Inserter(
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
    An entity that can move items between machines.

    .. NOTE::

        In Factorio, the ``Inserter`` prototype includes both regular and filter
        inserters. In Draftsman, inserters are split into two different classes,
        :py:class:`~.Inserter` and :py:class:`~.FilterInserter`
    """

    class Format(
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

        model_config = ConfigDict(title="Inserter")

    def __init__(
        self,
        name: str = inserters[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        override_stack_size: uint8 = None,
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
        super().__init__(
            name,
            inserters,
            position=position,
            tile_position=tile_position,
            direction=direction,
            override_stack_size=override_stack_size,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__
