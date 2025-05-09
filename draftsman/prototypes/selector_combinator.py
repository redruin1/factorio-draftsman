# selector_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    AttrsSignalID,
    QualityFilter,
    QualityName,
    Comparator,
    int32,
    uint32,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import selector_combinators

import attrs
from typing import Literal, Optional

SelectorOperations = Literal[
    "select",
    "count",
    "random",
    "stack-size",
    "rocket-capacity",
    "quality-filter",
    "quality-transfer",
]


@fix_incorrect_pre_init
@attrs.define
class SelectorCombinator(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity which has a number of useful miscellaneous combinator functions.
    """

    # class Format(
    #     PlayerDescriptionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         operation: Literal[
    #             "select",
    #             "count",
    #             "random",
    #             "stack-size",
    #             "rocket-capacity",
    #             "quality-filter",
    #             "quality-transfer",
    #         ] = Field(
    #             "select", description="""The master mode of the selector combinator."""
    #         )

    #         # Mode: "select"
    #         select_max: Optional[bool] = Field(
    #             True,
    #             description="""Whether or not to sort max to min when "mode" is "select".""",
    #         )
    #         index_constant: Optional[
    #             uint32
    #         ] = Field(  # TODO: which of these superceeds the other?
    #             0,
    #             description="""The constant input index to return when "mode" is "select".""",
    #         )
    #         index_signal: Optional[SignalID] = Field(
    #             None,
    #             description="""An input signal to use as an index, if specified.""",
    #         )

    #         # Mode: "count"
    #         count_signal: Optional[SignalID] = Field(
    #             None,
    #             description="""The signal with which to count the values of all inputs into.""",
    #         )

    #         # Mode: "random"
    #         random_update_interval: Optional[uint32] = Field(
    #             0,
    #             description="""How many game ticks to wait before selecting a new random signal from the input.""",
    #         )

    #         # Mode: "quality-filter"
    #         quality_filter: Optional[QualityFilter] = Field(
    #             None,
    #             description="""Specification of what quality signals to pass through.""",
    #         )

    #         # Mode: "quality-transfer"
    #         select_quality_from_signal: Optional[bool] = Field(
    #             False,
    #             description="""Whether or not to select quality from a single signal or from each input signal.""",
    #         )
    #         quality_source_static: Optional[
    #             Literal["normal", "uncommon", "rare", "epic", "legendary"]
    #         ] = Field("normal", description="""TODO""")
    #         quality_source_signal: Optional[SignalID] = Field(
    #             None, description="""TODO"""
    #         )
    #         quality_destination_signal: Optional[SignalID] = Field(
    #             None, description="""TODO"""
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="SelectorCombinator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(selector_combinators),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Optional[Direction] = Direction.NORTH,
    #     player_description: Optional[str] = None,
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
    #         similar_entities=selector_combinators,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         player_description=player_description,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return selector_combinators

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    operation: SelectorOperations = attrs.field(
        default="select", validator=one_of(SelectorOperations), metadata={"omit": False}
    )
    """
    The mode of operation that this selector is currently configured to perform.
    """

    # =========================================================================
    # Mode: "select"
    # =========================================================================

    select_max: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to sort the given signals in ascending or descending order
    when :py:attr:`.operation` is ``"select"``.
    """

    index_constant: int32 = attrs.field(default=0, validator=instance_of(int32))
    """
    Which constant signal index to output from the list of given signals when
    :py:attr:`.operation` is ``"select"``. 0-indexed; negative values are valid
    but unused. Overwritten by :py:attr:`.index_signal` if both are present
    simultaneously.
    """

    index_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    Which input signal to pull the index value from in order to select from the
    other input signals when :py:attr:`.operation` is ``"select"``. 0-indexed;
    negative values are valid but unused. Overwrites :py:attr:`.index_constant`
    if both are present simultaneously.
    """

    # =========================================================================
    # Mode: "count"
    # =========================================================================

    count_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to output the sum total number of unique signals on the input to.
    Note that this counts the number of different signals, not the total sum of 
    their given values.
    """

    # =========================================================================
    # Mode: "random"
    # =========================================================================

    random_update_interval: uint32 = attrs.field(
        default=0, validator=instance_of(uint32)
    )
    """
    Number of game ticks to wait before selecting a new random signal from the
    input. Can select the same signal multiple times sequentially.
    """

    # =========================================================================
    # Mode: "quality-filter"
    # =========================================================================

    quality_filter: QualityFilter = attrs.field(
        factory=QualityFilter, validator=instance_of(QualityFilter)
    )
    """
    The specification to filter the given input signals. Can select a specific 
    quality, or an inclusive range of qualities.
    """

    # =========================================================================
    # Mode: "quality-transfer"
    # =========================================================================

    select_quality_from_signal: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not to select quality from a single signal or from every input 
    signal. If this value is ``False`` the selector uses each signal in "Direct
    Selection" mode, and uses "Select from signal" when this value is ``True``.
    """

    quality_source_static: QualityName = attrs.field(  # TODO: should not include "any"
        default="normal", validator=one_of(QualityName)
    )
    """
    The quality to use when :py:attr:`.select_quality_from_signal` is ``False``.
    The selector will consider all signals with this specific quality.
    """

    quality_source_signal: Optional[
        AttrsSignalID
    ] = attrs.field(  # TODO: SignalID, but no quality!
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The input signal type to pull the quality from dynamically, if 
    :py:attr:`.select_quality_from_signal` is ``True``. 
    """

    quality_destination_signal: Optional[
        AttrsSignalID
    ] = attrs.field(  # TODO: SignalID, but no quality!
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(
            Optional[AttrsSignalID]
        ),  # TODO: validate it can only be each
    )
    """
    The destination signal(s) to output with the read quality value. Can be any
    fixed signal, as well as the wildcard ``"signal-each"``.
    """

    # =========================================================================

    def set_mode_select(
        self,
        select_max: bool = True,
        index_constant: int32 = 0,
        index_signal: Optional[AttrsSignalID] = None,
    ):
        """
        Sets the selector combinator to "Select Inputs" mode, along with
        associated parameters.

        :param select_max: Whether or not to sort signal values ascending or
            descending.
        :param index_constant: The constant signal index to use. Overwritten by
            ``index_signal`` if specified.
        :param index_signal: The signal to use the value from to get the indexed
            signal. If left ``None``, ``index_constant`` will be used instead.
        """
        self.operation = "select"
        self.select_max = select_max
        self.index_constant = index_constant
        self.index_signal = index_signal

    def set_mode_count(self, count_signal: Optional[AttrsSignalID] = None):
        """
        Sets the selector combinator to "Count Inputs" mode, along with
        associated parameters.

        :param count_signal: The signal to sum the counted signal value into.
            Will be empty if set to ``None``.
        """
        self.operation = "count"
        self.count_signal = count_signal

    def set_mode_random(self, interval: uint32 = 0):
        """
        Sets the selector combinator to "Random Input" mode, along with
        associated parameters.

        :param interval: The amount of ticks to wait between random signal
            selections.
        """
        self.operation = "random"
        self.random_update_interval = interval

    def set_mode_stack_size(self):
        """
        Sets the selector combintor to "Stack Size" mode.
        """
        self.operation = "stack-size"

    def set_mode_rocket_capacity(self):
        """
        Sets the selector combintor to "Rocket Capacity" mode.
        """
        self.operation = "rocket-capacity"

    def set_mode_quality_filter(
        self, quality: QualityName = "any", comparator: Comparator = "="
    ):
        """
        Sets the selector combintor to "Quality Filter" mode, along with
        associated parameters.

        :param quality: The quality to select, or the fixed half of the range of
            qualities to select if comparator is not ``"="``.
        :param comparator: The comparison operator to use when selecting quality
            signals.
        """
        self.operation = "quality-filter"
        self.quality_filter = QualityFilter(quality=quality, comparator=comparator)

    def set_mode_quality_transfer(
        self,
        select_quality_from_signal: bool = False,
        source_static: QualityName = "normal",  # TODO: QualityName no "any"
        source_signal: Optional[AttrsSignalID] = None,  # TODO: SignalID no quality
        destination_signal: Optional[AttrsSignalID] = None,  # TODO: SignalID no quality
    ):
        """
        Sets the selector combintor to "Quality Transfer" mode, along with
        associated parameters.

        :param select_quality_from_signal: Whether or not to use ``source_static``
            (``False``) or ``source_signal`` (``True``) when under operation.
        :param source_static: A fixed quality value to map inputs to.
        :param source_signal: A signal to grab the quality signifier from
            dynamically during operation.
        :param destination_signal: The target signal(s) to output with the
            extraced quality flag. Can be any fixed signal or the wildcard
            ``"signal-each"``.
        """
        self.operation = "quality-transfer"
        self.select_quality_from_signal = select_quality_from_signal
        self.quality_source_static = source_static
        self.quality_source_signal = source_signal
        self.quality_destination_signal = destination_signal

    def wipe_settings(self):
        """
        Resets all of the control behavior settings of this combinator to their
        default values.
        """
        self.operation = "select"

        self.select_max = True
        self.index_constant = 0
        self.index_signal = None

        self.count_signal = None

        self.random_update_interval = 0

        self.quality_filter = QualityFilter()

        self.select_quality_from_signal = False
        self.quality_source_static = "normal"
        self.quality_source_signal = None
        self.quality_destination_signal = None

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {
    #     "$id": "factorio:entity:selector_combinator"
    # },
    SelectorCombinator,
    lambda fields: {
        ("control_behavior", "operation"): fields.operation.name,
        ("control_behavior", "select_max"): fields.select_max.name,
        ("control_behavior", "index_constant"): fields.index_constant.name,
        ("control_behavior", "index_signal"): fields.index_signal.name,
        ("control_behavior", "count_inputs_signal"): fields.count_signal.name,
        (
            "control_behavior",
            "random_update_interval",
        ): fields.random_update_interval.name,
        ("control_behavior", "quality_filter"): fields.quality_filter.name,
        (
            "control_behavior",
            "select_quality_from_signal",
        ): fields.select_quality_from_signal.name,
        (
            "control_behavior",
            "quality_source_static",
        ): fields.quality_source_static.name,
        (
            "control_behavior",
            "quality_source_signal",
        ): fields.quality_source_signal.name,
        (
            "control_behavior",
            "quality_destination_signal",
        ): fields.quality_destination_signal.name,
    },
)
