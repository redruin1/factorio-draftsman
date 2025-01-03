# inserter.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import DraftsmanBaseModel, uint8
from draftsman.utils import get_first

from draftsman.data.entities import inserters

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Inserter(
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
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
        CircuitEnableMixin.Format,
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
            CircuitEnableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        pickup_position: Optional[list[float]] = Field(
            None,
            description="""The pickup position to use."""
        )
        drop_position: Optional[list[float]] = Field(
            None,
            description="""Teh drop position to use."""
        )

        model_config = ConfigDict(title="Inserter")

    def __init__(
        self,
        name: Optional[str] = get_first(inserters),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        pickup_position: Optional[list[float]] = None,
        drop_position: Optional[list[float]] = None,
        override_stack_size: uint8 = None,
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
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
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.pickup_position = pickup_position
        self.drop_position = drop_position

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def pickup_position(self) -> Optional[list[float]]:
        """
        The pickup position of the inserter.

        TODO
        """
        return self._root.pickup_position
    
    @pickup_position.setter
    def pickup_position(self, value: Optional[list[float]]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "pickup_position",
                value,
            )
            self._root.pickup_position = result
        else:
            self._root.pickup_position = value

    # =========================================================================

    @property
    def drop_position(self) -> Optional[list[float]]:
        """
        The pickup position of the inserter.

        TODO
        """
        return self._root.drop_position
    
    @drop_position.setter
    def drop_position(self, value: Optional[list[float]]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "drop_position",
                value,
            )
            self._root.drop_position = result
        else:
            self._root.drop_position = value

    # =========================================================================

    __hash__ = Entity.__hash__
