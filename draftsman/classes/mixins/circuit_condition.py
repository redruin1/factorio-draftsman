# circuit_condition.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from typing import Union


class CircuitConditionMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to have an circuit enable condition, such as when the
    value of some signal exceeds some constant.
    """

    def set_circuit_condition(self, a=None, cmp="<", b=0):
        # type: (str, str, Union[str, int]) -> None
        """
        Sets the circuit condition of the Entity.

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
        self._set_condition("circuit_condition", a, cmp, b)

    def remove_circuit_condition(self):
        # type: () -> None
        """
        Removes the circuit condition of the Entity. Does nothing if the Entity
        has no circuit condition to remove.
        """
        self.control_behavior.pop("circuit_condition", None)
