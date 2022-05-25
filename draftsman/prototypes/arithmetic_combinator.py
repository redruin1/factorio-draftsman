# arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.error import DataFormatError
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import arithmetic_combinators

from schema import SchemaError
import six
from typing import Union
import warnings


class ArithmeticCombinator(
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
):
    """
    An arithmetic combinator. Peforms a mathematical or bitwise operation on
    circuit signals.
    """

    def __init__(self, name=arithmetic_combinators[0], **kwargs):
        # type: (str, **dict) -> None
        super(ArithmeticCombinator, self).__init__(
            name, arithmetic_combinators, **kwargs
        )

        self._dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def first_operand(self):
        # type: () -> Union[str, int]
        """
        The first operand of the ``ArithmeticCombinator``.

        :getter: Gets the first operand of the operation, or ``None`` if not set.
        :setter: Sets the first operand of the operation. Removes the key if set
            to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
            ``str`` name of a valid signal, an ``int``, or ``None``.
        """
        arithmetic_conditions = self.control_behavior.get("arithmetic_conditions", None)
        if not arithmetic_conditions:
            return None

        if "first_signal" in arithmetic_conditions:
            return arithmetic_conditions["first_signal"]
        elif "first_constant" in arithmetic_conditions:
            return arithmetic_conditions["first_constant"]
        else:
            return None

    @first_operand.setter
    def first_operand(self, value):
        # type: (Union[dict, int]) -> None
        try:
            value = signatures.SIGNAL_ID_OR_CONSTANT.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]

        if value is None:  # Default
            arithmetic_conditions.pop("first_signal", None)
            arithmetic_conditions.pop("first_constant", None)
        elif isinstance(value, dict):  # Signal Dict
            arithmetic_conditions["first_signal"] = value
            arithmetic_conditions.pop("first_constant", None)
        else:  # Constant
            arithmetic_conditions["first_constant"] = value
            arithmetic_conditions.pop("first_signal", None)

    # =========================================================================

    @property
    def operation(self):
        # type: () -> str
        """
        The operation of the ``ArithmeticCombinator`` Can be one of:

        .. code-block:: python

            ["*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"]

        or ``None``. If the letter operations are specified as lowercase, they
        are automatically converted to uppercase on set.

        :getter: Gets the current operation, or ``None`` if not set.
        :setter: Sets the current operation. Removes the key if set to ``None``.
        :type: ``str``

        :exception TypeError: If set to anything other than one of the values
            specified above.
        """
        arithmetic_conditions = self.control_behavior.get("arithmetic_conditions", None)
        if not arithmetic_conditions:
            return None

        return arithmetic_conditions.get("operation", None)

    @operation.setter
    def operation(self, value):
        # type: (str) -> None
        try:
            value = signatures.OPERATION.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]

        if value is None:
            arithmetic_conditions.pop("operation", None)
        else:
            arithmetic_conditions["operation"] = value

    # =========================================================================

    @property
    def second_operand(self):
        # type: () -> Union[dict, int]
        """
        The second operand of the ``ArithmeticCombinator``.

        :getter: Gets the second operand of the operation, or ``None`` if not
            set.
        :setter: Sets the second operand of the operation. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
            ``str`` name of a valid signal, an ``int``, or ``None``.
        """
        arithmetic_conditions = self.control_behavior.get("arithmetic_conditions", None)
        if not arithmetic_conditions:
            return None

        if "second_signal" in arithmetic_conditions:
            return arithmetic_conditions["second_signal"]
        elif "second_constant" in arithmetic_conditions:
            return arithmetic_conditions["second_constant"]
        else:
            return None

    @second_operand.setter
    def second_operand(self, value):
        # type: (Union[str, int]) -> None
        try:
            value = signatures.SIGNAL_ID_OR_CONSTANT.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]

        if value is None:  # Default
            arithmetic_conditions.pop("second_signal", None)
            arithmetic_conditions.pop("second_constant", None)
        elif isinstance(value, dict):  # Signal Dict
            arithmetic_conditions["second_signal"] = value
            arithmetic_conditions.pop("second_constant", None)
        else:  # Constant
            arithmetic_conditions["second_constant"] = value
            arithmetic_conditions.pop("second_signal", None)

    # =========================================================================

    @property
    def output_signal(self):
        # type: () -> dict
        """
        The output signal of the ``ArithmeticCombinator``.

        :getter: Gets the output signal, or ``None`` if not set.
        :setter: Sets the output signal. Removes the key if set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
            ``None``.
        """
        arithmetic_conditions = self.control_behavior.get("arithmetic_conditions", None)
        if not arithmetic_conditions:
            return None

        return arithmetic_conditions.get("output_signal", None)

    @output_signal.setter
    def output_signal(self, value):
        # type: (str) -> None
        try:
            value = signatures.SIGNAL_ID_OR_NONE.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]

        if value is None:  # Default
            arithmetic_conditions.pop("output_signal", None)
        else:  # Signal Dict
            arithmetic_conditions["output_signal"] = value

    # =========================================================================

    def set_arithmetic_conditions(self, a=None, op="*", b=0, out=None):
        # type: (Union[str, int], str, Union[str, int], str) -> None
        """
        Sets the entire arithmetic condition of the ArithmeticCombinator.

        :param a: The name of the first signal to set, some constant, or ``None``.
        :param op: The string representation of the operation to perform, as
            specified above.
        :param b: The name of the second signal to set, some constant, or ``None``.
        :param out: The name of the output signal to set, or ``None``.

        :exception DataFormatError: If any argument fails to match the formats
            specified above.
        """

        # Check all the parameters before we set anything to preserve original
        try:
            a = signatures.SIGNAL_ID_OR_CONSTANT.validate(a)
            op = signatures.OPERATION.validate(op)
            b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
            out = signatures.SIGNAL_ID_OR_NONE.validate(out)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]

        # A
        if a is None:  # Default
            arithmetic_conditions.pop("first_signal", None)
            arithmetic_conditions.pop("first_constant", None)
        elif isinstance(a, dict):  # Signal Dict
            arithmetic_conditions["first_signal"] = a
            arithmetic_conditions.pop("first_constant", None)
        else:  # Constant
            arithmetic_conditions["first_constant"] = a
            arithmetic_conditions.pop("first_signal", None)

        # op
        if op is None:
            arithmetic_conditions.pop("operation", None)
        else:
            arithmetic_conditions["operation"] = op

        # B
        if b is None:  # Default
            arithmetic_conditions.pop("second_signal", None)
            arithmetic_conditions.pop("second_constant", None)
        elif isinstance(b, dict):  # Signal Dict
            arithmetic_conditions["second_signal"] = b
            arithmetic_conditions.pop("second_constant", None)
        else:  # Constant
            arithmetic_conditions["second_constant"] = b
            arithmetic_conditions.pop("second_signal", None)

        # out
        if out is None:  # Default
            arithmetic_conditions.pop("output_signal", None)
        else:  # Signal Dict
            arithmetic_conditions["output_signal"] = out

    def remove_arithmetic_conditions(self):
        # type: () -> None
        """
        Removes the entire ``"arithmetic_conditions"`` key from the control
        behavior.
        """
        self.control_behavior.pop("arithmetic_conditions", None)
