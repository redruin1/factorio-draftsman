# circuit_condition.py

from draftsman.signatures import Condition, SignalID, int32

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


class CircuitConditionMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)
    Allows the Entity to have an circuit enable condition, such as when the
    value of some signal exceeds some constant.
    """

    class ControlFormat(BaseModel):
        circuit_condition: Optional[Condition] = Field(
            Condition(first_signal=None, comparator="<", constant=0),
            description="""
            The circuit condition that must be passed in order for this entity
            to function, if configured to do so.
            """,
        )

    class Format(BaseModel):
        pass

    def set_circuit_condition(
        self,
        a: Union[SignalID, None] = None,
        cmp: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
        b: Union[SignalID, int32] = 0,
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
        self._set_condition("circuit_condition", a, cmp, b)

    def remove_circuit_condition(self):
        """
        Removes the circuit condition of the Entity. Does nothing if the Entity
        has no circuit condition to remove.
        """
        # self.control_behavior.pop("circuit_condition", None)
        self.control_behavior.circuit_condition = None
