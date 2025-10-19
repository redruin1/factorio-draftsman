# selector_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    SignalID,
    SignalIDBase,
    QualityFilter,
    QualityID,
    Comparator,
    int32,
    uint32,
)
from draftsman.validators import conditional, instance_of, one_of
from draftsman.warning import PureVirtualDisallowedWarning

from draftsman.data import signals
from draftsman.data.entities import selector_combinators

import attrs
from typing import Literal, Optional
import warnings

SelectorOperations = Literal[
    "select",
    "count",
    "random",
    "stack-size",
    "rocket-capacity",
    "quality-filter",
    "quality-transfer",
]


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
    .. versionadded:: 3.0.0 (Factorio 2.0)

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
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The mode of operation that this selector is currently configured to perform.
    """

    # =========================================================================
    # Mode: "select"
    # =========================================================================

    select_max: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to sort the given signals in ascending or descending order
    when :py:attr:`.operation` is ``"select"``.

    .. seealso::

        :py:meth:`.set_mode_select`
    """

    index_constant: int32 = attrs.field(default=0, validator=instance_of(int32))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Which constant signal index to output from the list of given signals when
    :py:attr:`.operation` is ``"select"``. 0-indexed; negative values are valid
    but unused. Overwritten by :py:attr:`.index_signal` if both are present
    simultaneously.

    .. seealso::

        :py:meth:`.set_mode_select`
    """

    index_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Which input signal to pull the index value from in order to select from the
    other input signals when :py:attr:`.operation` is ``"select"``. 0-indexed;
    negative values are valid but unused. Overwrites :py:attr:`.index_constant`
    if both are present simultaneously.

    .. seealso::

        :py:meth:`.set_mode_select`
    """

    # =========================================================================
    # Mode: "count"
    # =========================================================================

    count_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    What signal to output the sum total number of unique signals on the input to.
    Note that this counts the number of different signals, not the total sum of 
    their given values.

    .. seealso::

        :py:meth:`.set_mode_count`
    """

    # =========================================================================
    # Mode: "random"
    # =========================================================================

    random_update_interval: uint32 = attrs.field(
        default=0, validator=instance_of(uint32)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Number of game ticks to wait before selecting a new random signal from the
    input. Can select the same signal multiple times sequentially.

    .. seealso::

        :py:meth:`.set_mode_random`
    """

    # =========================================================================
    # Mode: "quality-filter"
    # =========================================================================

    quality_filter: QualityFilter = attrs.field(
        factory=QualityFilter, validator=instance_of(QualityFilter)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The specification to filter the given input signals. Can select a specific 
    quality, or an inclusive range of qualities.

    .. seealso::

        :py:meth:`.set_mode_quality_filter`
    """

    # =========================================================================
    # Mode: "quality-transfer"
    # =========================================================================

    select_quality_from_signal: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to select quality from a single signal or from every input 
    signal. If this value is ``False`` the selector uses each signal in "Direct
    Selection" mode, and uses "Select from signal" when this value is ``True``.

    .. seealso::

        :py:meth:`.set_mode_quality_transfer`
    """

    quality_source_static: QualityID = attrs.field(
        default="normal", validator=one_of(QualityID)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The quality to use when :py:attr:`.select_quality_from_signal` is ``False``.
    The selector will consider all signals with this specific quality.

    .. seealso::

        :py:meth:`.set_mode_quality_transfer`
    """

    quality_source_signal: Optional[SignalIDBase] = attrs.field(
        default=None,
        converter=SignalIDBase.converter,
        validator=instance_of(Optional[SignalIDBase]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The input signal type to pull the quality from dynamically, if 
    :py:attr:`.select_quality_from_signal` is ``True``. 

    .. seealso::

        :py:meth:`.set_mode_quality_transfer`
    """

    quality_destination_signal: Optional[SignalIDBase] = attrs.field(
        default=None,
        converter=SignalIDBase.converter,
        validator=instance_of(Optional[SignalIDBase]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The destination signal(s) to output with the read quality value. Can be any
    fixed signal, as well as the wildcard ``"signal-each"``.

    .. seealso::

        :py:meth:`.set_mode_quality_transfer`
    """

    @quality_destination_signal.validator
    @conditional(ValidationMode.STRICT)
    def _quality_destination_signal_validator(
        self, attr: attrs.Attribute, value: Optional[SignalIDBase]
    ):
        """
        Ensure that (if a pure virtual signal is provided) only ``signal-each``
        is a valid input.
        """
        if value is None:
            return
        if value.name in signals.pure_virtual and value.name != "signal-each":
            msg = "Cannot set this signal to '{}'; only permitted pure virtual signal is 'signal-each'".format(
                value.name
            )
            warnings.warn(PureVirtualDisallowedWarning(msg))

    # =========================================================================

    def set_mode_select(
        self,
        select_max: bool = True,
        index_constant: int = 0,  # TODO: should be int32
        index_signal: Optional[str] = None,  # TODO: should be SignalID
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

    def set_mode_count(self, count_signal: Optional[SignalID] = None):
        """
        Sets the selector combinator to "Count Inputs" mode, along with
        associated parameters.

        :param count_signal: The signal to sum the counted signal value into.
            Will be empty if set to ``None``.
        """
        self.operation = "count"
        self.count_signal = count_signal

    def set_mode_random(self, interval: int = 0):  # TODO: should be uint32
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
        self, quality: Optional[QualityID] = None, comparator: Comparator = "="
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
        source_static: QualityID = "normal",
        source_signal: Optional[SignalIDBase] = None,
        destination_signal: Optional[SignalIDBase] = None,
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
