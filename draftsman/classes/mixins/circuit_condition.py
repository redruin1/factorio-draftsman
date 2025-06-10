# circuit_condition.py

from draftsman.classes.mixins.control_behavior import ControlBehaviorMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Comparator, Condition, SignalID, int32
from draftsman.validators import instance_of

import attrs
from typing import Union


@attrs.define(slots=False)
class CircuitConditionMixin(ControlBehaviorMixin):
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)
    Allows the Entity to have an circuit enable condition, such as when the
    value of some signal exceeds some constant.
    """

    circuit_condition: Condition = attrs.field(
        factory=Condition,
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    The circuit condition that must be passed in order for this entity
    to function, if configured to do so.
    """

    # =========================================================================

    def set_circuit_condition(
        self,
        first_operand: Union[SignalID, None] = None,
        comparator: Comparator = "<",
        second_operand: Union[SignalID, int32] = 0,
    ):
        """
        Sets the circuit condition of the Entity.
        ``cmp`` can be specified as stored as the single unicode character which
        is used by Factorio, or you can use the Python formatted 2-character
        equivalents::
            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they will remain that way until
        exported to a dict or blueprint string.

        :param a: The first signal, it's name, or ``None``.
        :param cmp: The comparator string.
        :param b: The second signal, it's name, or some integer constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        self._set_condition(
            "circuit_condition", first_operand, comparator, second_operand
        )

    def merge(self, other: "CircuitConditionMixin"):
        super().merge(other)

        self.circuit_condition = other.circuit_condition


draftsman_converters.add_hook_fns(
    CircuitConditionMixin,
    lambda fields: {
        ("control_behavior", "circuit_condition"): fields.circuit_condition.name,
    },
)
