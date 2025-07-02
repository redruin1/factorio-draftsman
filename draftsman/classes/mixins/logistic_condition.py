# logistic_condition.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Comparator, Condition, SignalID, int32
from draftsman.validators import instance_of

import attrs
from typing import Union


@attrs.define(slots=False)
class LogisticConditionMixin(Exportable):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to have an logistic enable condition, such as when the
    amount of some item in the logistic network exceeds some constant.
    """

    connect_to_logistic_network: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )

    # =========================================================================

    logistic_condition: Condition = attrs.field(
        factory=lambda: Condition(first_signal=None, comparator="<", constant=0),
        converter=Condition.converter,
        validator=instance_of(Condition),
    )
    """
    The logistic condition that must be passed in order for this entity to 
    function, if configured to do so.
    """

    # =========================================================================

    def set_logistic_condition(
        self,
        first_operand: Union[SignalID, None] = None,
        comparator: Comparator = "<",
        second_operand: Union[SignalID, int32] = 0,
    ):
        """
        Sets the logistic condition of the Entity.

        ``cmp`` can be specified as stored as the single unicode character which
        is used by Factorio, or you can use the Python formatted 2-character
        equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they are converted to and stored as
        the first format.

        :param first_operand: The string name of the first signal.
        :param comparator: The operation to use, as specified above.
        :param second_operand: The string name of the second signal, or some
            32-bit constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``comparator`` is not a valid operation, or if ``b`` is neither a
            valid signal name nor a constant.
        """
        self._set_condition(
            "logistic_condition", first_operand, comparator, second_operand
        )

    def merge(self, other: "LogisticConditionMixin"):
        super().merge(other)
        self.connect_to_logistic_network = other.connect_to_logistic_network
        self.logistic_condition = other.logistic_condition


draftsman_converters.add_hook_fns(
    LogisticConditionMixin,
    lambda fields: {
        (
            "control_behavior",
            "connect_to_logistic_network",
        ): fields.connect_to_logistic_network.name,
        ("control_behavior", "logistic_condition"): fields.logistic_condition.name,
    },
)
