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
    An entity which has a number of miscellaneous circuit functions.
    """

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

    quality_source_static: QualityName = attrs.field(
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

    # TODO: SignalID, but no quality!
    quality_destination_signal: Optional[
        AttrsSignalID
    ] = attrs.field(
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
        self, quality: Optional[QualityName] = None, comparator: Comparator = "="
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
        source_static: QualityName = "normal",
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


SelectorCombinator.add_schema(None, version=(1, 0))

SelectorCombinator.add_schema(
    {
        "$id": "urn:factorio:entity:selector-combinator",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "operation": {
                        "enum": [
                            "select",
                            "count",
                            "random",
                            "stack-size",
                            "rocket-capacity",
                            "quality-filter",
                            "quality-transfer",
                        ],
                        "default": "select",
                    },
                    "select_max": {"type": "boolean", "default": "true"},
                    "index_constant": {"$ref": "urn:int32", "default": 0},
                    "index_signal": {
                        "oneOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },  # TODO: nullable?
                    "count_inputs_signal": {
                        "oneOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },  # TODO: nullable?,
                    "random_update_interval": {"$ref": "urn:uint32", "default": 0},
                    "quality_filter": {},
                    "select_quality_from_signal": {
                        "type": "boolean",
                        "default": "false",
                    },
                    "quality_source_static": {
                        "$ref": "urn:factorio:quality-name",
                        "default": "normal",
                    },
                    "quality_source_signal": {
                        "oneOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },  # TODO: nullable?,
                    "quality_destination_signal": {
                        "oneOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },  # TODO: nullable?,
                },
            }
        },
    }
)

draftsman_converters.add_hook_fns(
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
