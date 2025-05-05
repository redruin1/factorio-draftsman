# logistic_condition.py

from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSimpleCondition, AttrsSignalID, int32
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


@attrs.define(slots=False)
class LogisticConditionMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to have an logistic enable condition, such as when the
    amount of some item in the logistic network exceeds some constant.
    """

    # =========================================================================

    connect_to_logistic_network: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )

    # @property
    # def connect_to_logistic_network(self) -> bool:
    #     """
    #     Whether or not this entity should use it's logistic network condition to
    #     control its operation (if it has one).

    #     :getter: Gets the value of ``connect_to_logistic_network``, or ``None``
    #         if not set.
    #     :setter: Sets the value of ``connect_to_logistic_network``. Removes the
    #         key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.connect_to_logistic_network

    # @connect_to_logistic_network.setter
    # def connect_to_logistic_network(self, value: bool):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "connect_to_logistic_network",
    #             value,
    #         )
    #         self.control_behavior.connect_to_logistic_network = result
    #     else:
    #         self.control_behavior.connect_to_logistic_network = value

    # =========================================================================

    logistic_condition: AttrsSimpleCondition = attrs.field(
        factory=lambda: AttrsSimpleCondition(
            first_signal=None, comparator="<", constant=0
        ),
        converter=AttrsSimpleCondition.converter,
        validator=instance_of(AttrsSimpleCondition),
    )
    """
    The logistic condition that must be passed in order for this entity to 
    function, if configured to do so.
    """

    # =========================================================================

    def set_logistic_condition(
        self,
        first_operand: Union[AttrsSignalID, None] = None,
        comparator: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
        second_operand: Union[AttrsSignalID, int32] = 0,
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

        :param a: The string name of the first signal.
        :param cmp: The operation to use, as specified above.
        :param b: The string name of the second signal, or some 32-bit constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        self._set_condition(
            "logistic_condition", first_operand, comparator, second_operand
        )

    # def remove_logistic_condition(self):
    #     """
    #     Removes the logistic condition of the Entity. Does nothing if the Entity
    #     has no logistic condition to remove.
    #     """
    #     self.logistic_condition = None

    def merge(self, other: "LogisticConditionMixin"):
        super().merge(other)
        self.connect_to_logistic_network = other.connect_to_logistic_network
        self.logistic_condition = other.logistic_condition


# TODO: versioning
draftsman_converters.add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:logistic_condition",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "connect_to_logistic_network": {
                        "type": "boolean",
                        "default": "false",
                    },
                    "logistic_condition": {"$ref": "factorio:simple_condition"},
                },
            }
        },
    },
    LogisticConditionMixin,
    lambda fields: {
        (
            "control_behavior",
            "connect_to_logistic_network",
        ): fields.connect_to_logistic_network.name,
        ("control_behavior", "logistic_condition"): fields.logistic_condition.name,
    },
)
