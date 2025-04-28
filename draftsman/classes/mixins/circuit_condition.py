# circuit_condition.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Condition, AttrsSimpleCondition, AttrsSignalID, int32
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


@attrs.define(slots=False)
class CircuitConditionMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)
    Allows the Entity to have an circuit enable condition, such as when the
    value of some signal exceeds some constant.
    """

    class ControlFormat(BaseModel):
        circuit_condition_enabled: Optional[bool] = Field(
            False,
            description="""
            Whether or not the entity is controlled by the specified circuit
            condition, if present.
            """,
        )
        circuit_condition: Optional[Condition] = Field(
            Condition(first_signal=None, comparator="<", constant=0),
            description="""
            The circuit condition that must be passed in order for this entity
            to function, if configured to do so.
            """,
        )

    class Format(BaseModel):
        pass

    # =========================================================================

    # circuit_enabled: bool = attrs.field(
    #     default=False,
    #     validator=attrs.validators.instance_of(bool),
    #     metadata={"location": ("control_behavior", "circuit_enabled")},
    # )
    # """
    # Whether or not the entity is controlled by the specified circuit
    # condition, if present.
    # """

    # @property
    # def circuit_enabled(self) -> Optional[bool]:
    #     """
    #     Whether or not the machine enables its operation based on a circuit
    #     condition. Only used on entities that have multiple operation states,
    #     including (but not limited to) a inserters, belts, train-stops,
    #     power-switches, etc.

    #     :getter: Gets the value of ``circuit_enabled``, or ``None`` if not set.
    #     :setter: Sets the value of ``circuit_enabled``. Removes the attribute if
    #         set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.circuit_enabled

    # @circuit_enabled.setter
    # def circuit_enabled(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_enabled",
    #             value,
    #         )
    #         self.control_behavior.circuit_enabled = result
    #     else:
    #         self.control_behavior.circuit_enabled = value

    # =========================================================================

    circuit_condition: AttrsSimpleCondition = attrs.field(
        default=AttrsSimpleCondition(first_signal=None, comparator="<", constant=0),
        converter=AttrsSimpleCondition.converter,
        validator=instance_of(AttrsSimpleCondition),
    )
    """
    The circuit condition that must be passed in order for this entity
    to function, if configured to do so.
    """

    # =========================================================================

    def set_circuit_condition(
        self,
        first_operand: Union[AttrsSignalID, None] = None,
        comparator: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
        second_operand: Union[AttrsSignalID, int32] = 0,
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

    def remove_circuit_condition(self):
        """
        Removes the circuit condition of the Entity. Does nothing if the Entity
        has no circuit condition to remove.
        """
        # self.control_behavior.pop("circuit_condition", None)
        self.control_behavior.circuit_condition = None

    def merge(self, other: "CircuitConditionMixin"):
        super().merge(other)
        self.circuit_condition = other.circuit_condition


draftsman_converters.add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:circuit_condition",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    # "circuit_enabled": {
                    #     "type": "boolean",
                    #     "default": "false",
                    # },
                    "circuit_condition": {"$ref": "factorio:simple_condition"},
                },
            }
        },
    },
    CircuitConditionMixin,
    lambda fields: {
        # fields.circuit_enabled.name: ("control_behavior", "circuit_enabled"),
        ("control_behavior", "circuit_condition"): fields.circuit_condition.name,
    },
)
