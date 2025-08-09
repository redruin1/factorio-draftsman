# circuit_condition.py

from draftsman.classes.mixins.control_behavior import ControlBehaviorMixin
from draftsman.serialization import draftsman_converters
from draftsman import signatures
from draftsman.validators import instance_of

import attrs
from typing import Union


@attrs.define(slots=False)
class CircuitConditionMixin(ControlBehaviorMixin):
    """
    Allows the Entity to have an circuit condition (usually to enable it's
    function).
    """

    circuit_condition: signatures.Condition = attrs.field(
        factory=signatures.Condition,
        converter=signatures.Condition.converter,
        validator=instance_of(signatures.Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The circuit condition that must be passed in order for this entity
    to function, if configured to do so.
    """

    # =========================================================================

    def set_circuit_condition(
        self,
        first_operand: Union[signatures.SignalID, None] = None,
        comparator: signatures.Comparator = "<",
        second_operand: Union[signatures.SignalID, int] = 0, # TODO: should be int32
    ):
        """
        Sets the circuit condition of the Entity.
        ``comparator`` can be specified as stored as the single unicode
        character which is used by Factorio, or you can use the Python-style
        2-character equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they are converted to and stored as
        the first format.

        :param first_operand: The first signal, it's name, or ``None``.
        :param comparator: The comparator string.
        :param second_operand: The second signal, it's name, or some integer
            constant.

        :exception DataFormatError: If ``first_operand`` is not a valid signal
            name, if ``comparator`` is not a valid operation, or if
            ``second_operand`` is neither a valid signal name nor a constant.
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
