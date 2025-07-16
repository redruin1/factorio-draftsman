# selector_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import DraftsmanBaseModel, QualityFilter, SignalID, uint32
from draftsman.utils import get_first

from draftsman.data.entities import selector_combinators

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class SelectorCombinator(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity which has a number of miscellaneous combinator functions.
    """

    class Format(
        PlayerDescriptionMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(DraftsmanBaseModel):
            operation: Literal[
                "select",
                "count",
                "random",
                "stack-size",
                "rocket-capacity",
                "quality-filter",
                "quality-transfer",
            ] = Field(
                "select", description="""The master mode of the selector combinator."""
            )

            # Mode: "select"
            select_max: Optional[bool] = Field(
                True,
                description="""Whether or not to sort max to min when "mode" is "select".""",
            )
            index_constant: Optional[uint32] = (
                Field(  # TODO: which of these superceeds the other?
                    0,
                    description="""The constant input index to return when "mode" is "select".""",
                )
            )
            index_signal: Optional[SignalID] = Field(
                None,
                description="""An input signal to use as an index, if specified.""",
            )

            # Mode: "count"
            count_signal: Optional[SignalID] = Field(
                None,
                description="""The signal with which to count the values of all inputs into.""",
            )

            # Mode: "random"
            random_update_interval: Optional[uint32] = Field(
                0,
                description="""How many game ticks to wait before selecting a new random signal from the input.""",
            )

            # Mode: "quality-filter"
            quality_filter: Optional[QualityFilter] = Field(
                None,
                description="""Specification of what quality signals to pass through.""",
            )

            # Mode: "quality-transfer"
            select_quality_from_signal: Optional[bool] = Field(
                False,
                description="""Whether or not to select quality from a single signal or from each input signal.""",
            )
            quality_source_static: Optional[
                Literal["normal", "uncommon", "rare", "epic", "legendary"]
            ] = Field("normal", description="""TODO""")
            quality_source_signal: Optional[SignalID] = Field(
                None, description="""TODO"""
            )
            quality_destination_signal: Optional[SignalID] = Field(
                None, description="""TODO"""
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="SelectorCombinator")

    def __init__(
        self,
        name: Optional[str] = get_first(selector_combinators),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Optional[Direction] = Direction.NORTH,
        player_description: Optional[str] = None,
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
            similar_entities=selector_combinators,
            position=position,
            tile_position=tile_position,
            direction=direction,
            player_description=player_description,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    def set_mode(self):
        pass  # TODO: think about best way to do this

    # =========================================================================

    __hash__ = Entity.__hash__
