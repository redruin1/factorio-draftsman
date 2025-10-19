# splitter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Condition, SignalID
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import splitters

import attrs
from typing import Literal, Optional

try:
    from typing import Literal
except ImportError:  # pragma: no coverage
    from typing_extensions import Literal


@attrs.define
class Splitter(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    An entity that evenly splits a set of input belts between a set of output
    belts.
    """

    @property
    def similar_entities(self) -> list[str]:
        return splitters

    # =========================================================================

    input_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The side that receives input priority. Can be one of ``"left"``, ``"right"``, 
    or ``"none"``. Overridden if :py:attr:`.set_input_side` is ``True``.
    """

    # =========================================================================

    set_input_side: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not a connected circuit network should control what the input 
    priority side should be.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    input_left_condition: Condition = attrs.field(
        factory=lambda: Condition(first_signal="signal-I", comparator="<", constant=0),
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The condition where the splitter should prioritize left-side inputs. If both
    this condition and :py:attr:`.input_right_condition` evaluate to true at the
    same time, then the current input priority remains unchanged.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    input_right_condition: Condition = attrs.field(
        factory=lambda: Condition(first_signal="signal-I", comparator=">", constant=0),
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The condition where the splitter should prioritize right-side inputs. If both
    this condition and :py:attr:`.input_left_condition` evaluate to true at the
    same time, then the current input priority remains unchanged.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    output_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The side that receives output priority. Can be one of ``"left"``, ``"right"``, 
    or ``"none"``. Overridden if :py:attr:`.set_output_side` is ``True``.
    """

    # =========================================================================

    set_output_side: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not a connected circuit network should control what the output 
    priority side should be.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    output_left_condition: Condition = attrs.field(
        factory=lambda: Condition(first_signal="signal-O", comparator="<", constant=0),
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The condition where the splitter should prioritize left-side outputs. If both
    this condition and :py:attr:`.output_right_condition` evaluate to true at the
    same time, then the current output priority remains unchanged.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    output_right_condition: Condition = attrs.field(
        factory=lambda: Condition(first_signal="signal-O", comparator=">", constant=0),
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The condition where the splitter should prioritize right-side output. If both
    this condition and :py:attr:`.output_left_condition` evaluate to true at the
    same time, then the current output priority remains unchanged.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    filter: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Sets the Splitter's filter. If :py:attr:`.filter` is set but 
    :py:attr:`.output_priority` is not, then the output side defaults to 
    ``"left"``.
    """

    # =========================================================================

    set_filter: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this splitter should use the circuit network to determine
    what item to filter. If multiple signals are given, the selection process
    is equivalent to ``signal-any``.

    .. versionadded:: 3.2.0 (Factorio 2.0.67)
    """

    # =========================================================================

    def merge(self, other: "Splitter"):
        super().merge(other)

        self.input_priority = other.input_priority
        self.set_input_side = other.set_input_side
        self.input_left_condition = other.input_left_condition
        self.input_right_condition = other.input_right_condition

        self.output_priority = other.output_priority
        self.set_output_side = other.set_output_side
        self.output_left_condition = other.output_left_condition
        self.output_right_condition = other.output_right_condition

        self.filter = other.filter
        self.set_filter = other.set_filter

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Splitter,
    lambda fields: {
        "input_priority": fields.input_priority.name,
        "output_priority": fields.output_priority.name,
        "filter": (  # In 1.0, "filter" was just the name of a signal
            fields.filter,
            lambda input, _, inst, args: SignalID(input),
        ),
    },
    lambda fields, converter: {
        "input_priority": fields.input_priority.name,
        "output_priority": fields.output_priority.name,
        "filter": (fields.filter, lambda inst: getattr(inst.filter, "name", None)),
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Splitter,
    lambda fields: {
        "input_priority": fields.input_priority.name,
        ("control_behavior", "set_input_side"): fields.set_input_side.name,
        ("control_behavior", "input_left_condition"): fields.input_left_condition.name,
        (
            "control_behavior",
            "input_right_condition",
        ): fields.input_right_condition.name,
        "output_priority": fields.output_priority.name,
        ("control_behavior", "set_output_side"): fields.set_output_side.name,
        (
            "control_behavior",
            "output_left_condition",
        ): fields.output_left_condition.name,
        (
            "control_behavior",
            "output_right_condition",
        ): fields.output_right_condition.name,
        # In 2.0, "filter" is a fully qualified SignalID to handle quality ranges
        "filter": fields.filter.name,
    },
)
