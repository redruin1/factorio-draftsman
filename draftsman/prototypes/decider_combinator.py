# decider_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.error import DataFormatError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import decider_combinators

from schema import SchemaError
import six
from typing import Union
import warnings


class DeciderCombinator(
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
):
    """
    A decider combinator. Makes comparisons based on circuit network inputs.
    """

    def __init__(self, name=decider_combinators[0], **kwargs):
        # type: (str, **dict) -> None
        super(DeciderCombinator, self).__init__(name, decider_combinators, **kwargs)

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
        The first operand of the ``DeciderCombinator``.

        :getter: Gets the first operand of the operation, or ``None`` if not set.
        :setter: Sets the first operand of the operation. Removes the key if set
            to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
            ``None``.
        """
        decider_conditions = self.control_behavior.get("decider_conditions", None)
        if not decider_conditions:
            return None

        return decider_conditions.get("first_signal", None)

    @first_operand.setter
    def first_operand(self, value):
        # type: (Union[dict, int]) -> None
        try:
            value = signatures.SIGNAL_ID_OR_NONE.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        if value is None:  # Default
            decider_conditions.pop("first_signal", None)
        else:  # Signal Dict
            decider_conditions["first_signal"] = value

    # =========================================================================

    @property
    def operation(self):
        # type: () -> str
        """
        The operation of the ``DeciderCombinator`` Can be specified as stored as
        the single unicode character which is used by Factorio, or you can use
        the Python formatted 2-character equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        or ``None``. If specified in the second format, they are converted to
        and stored as the first format.

        :getter: Gets the current operation, or ``None`` if not set.
        :setter: Sets the current operation. Removes the key if set to ``None``.
        :type: ``str``

        :exception TypeError: If set to anything other than one of the values
            specified above.
        """
        decider_conditions = self.control_behavior.get("decider_conditions", None)
        if not decider_conditions:
            return None

        return decider_conditions.get("operation", None)

    @operation.setter
    def operation(self, value):
        # type: (str) -> None
        try:
            value = signatures.COMPARATOR.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        if value is None:
            decider_conditions.pop("operation", None)
        else:
            decider_conditions["operation"] = value

    # =========================================================================

    @property
    def second_operand(self):
        # type: () -> Union[dict, int]
        """
        The second operand of the ``DeciderCombinator``.

        :getter: Gets the second operand of the operation, or ``None`` if not
            set.
        :setter: Sets the second operand of the operation. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, an
            ``int``, or ``None``.
        """
        decider_conditions = self.control_behavior.get("decider_conditions", None)
        if not decider_conditions:
            return None

        if "second_signal" in decider_conditions:
            return decider_conditions["second_signal"]
        elif "constant" in decider_conditions:
            return decider_conditions["constant"]
        else:
            return None

    @second_operand.setter
    def second_operand(self, value):
        # type: (Union[str, int]) -> None
        try:
            value = signatures.SIGNAL_ID_OR_CONSTANT.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        if value is None:  # Default
            decider_conditions.pop("second_signal", None)
            decider_conditions.pop("constant", None)
        elif isinstance(value, dict):  # Signal Dict
            decider_conditions["second_signal"] = value
            decider_conditions.pop("constant", None)
        else:  # Constant
            decider_conditions["constant"] = value
            decider_conditions.pop("second_signal", None)

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
        decider_conditions = self.control_behavior.get("decider_conditions", None)
        if not decider_conditions:
            return None

        return decider_conditions.get("output_signal", None)

    @output_signal.setter
    def output_signal(self, value):
        # type: (str) -> None
        try:
            value = signatures.SIGNAL_ID_OR_NONE.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        if value is None:  # Default
            decider_conditions.pop("output_signal", None)
        else:  # Signal Dict
            decider_conditions["output_signal"] = value

    # =========================================================================

    @property
    def copy_count_from_input(self):
        # type: () -> bool
        """
        Whether or not the input value of a signal is transposed to the output
        signal. If this is false, the output signal is output with a value of 1
        if the condition is met.

        :getter: Gets whether or not to copy the value, or ``None`` is not set.
        :setter: Sets whether or not to copy the value. Removes the key if set
            to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        decider_conditions = self.control_behavior.get("decider_conditions", None)
        if not decider_conditions:
            return None

        return decider_conditions.get("copy_count_from_input", None)

    @copy_count_from_input.setter
    def copy_count_from_input(self, value):
        # type: (bool) -> None
        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        if value is None:
            decider_conditions.pop("copy_count_from_input", None)
        elif isinstance(value, bool):
            decider_conditions["copy_count_from_input"] = value
        else:
            raise TypeError("'copy_count_from_input' must be a bool or None")

    # =========================================================================

    def set_decider_conditions(self, a=None, cmp="<", b=0, out=None):
        # type: (Union[str, int], str, Union[str, int], str) -> None
        """
        Set the operation for the ``DeciderCombinator``.

        :param a: The first signal or ``None``, as specified in :py:data:`.SIGNAL_ID`.
        :param cmp: The comparison operator, as specified in :py:data:`.COMPARATOR`.
        :param b: The second signal, constant or ``None``, as specified in
            :py:data:`.SIGNAL_ID_OR_CONSTANT`..
        :param out: The output signal, or ``None``, as specified in
            :py:data:`.SIGNAL_ID_OR_NONE`.

        :exception DataFormatError: If the any of the arguments fail to match
            their correct formats.
        """
        # Check all the parameters before we set anything to preserve original
        try:
            a = signatures.SIGNAL_ID_OR_NONE.validate(a)
            cmp = signatures.COMPARATOR.validate(cmp)
            b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
            out = signatures.SIGNAL_ID_OR_NONE.validate(out)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        # A
        if a is None:  # Default
            decider_conditions.pop("first_signal", None)
        else:  # Signal Dict
            decider_conditions["first_signal"] = a

        # op
        if cmp is None:
            decider_conditions.pop("comparator", None)
        else:
            decider_conditions["comparator"] = cmp

        # B
        if b is None:  # Default
            decider_conditions.pop("second_signal", None)
            decider_conditions.pop("constant", None)
        elif isinstance(b, dict):  # Signal Dict
            decider_conditions["second_signal"] = b
            decider_conditions.pop("constant", None)
        else:  # Constant
            decider_conditions["constant"] = b
            decider_conditions.pop("second_signal", None)

        # out
        if out is None:  # Default
            decider_conditions.pop("output_signal", None)
        else:  # Signal Dict
            decider_conditions["output_signal"] = out

    def remove_decider_conditions(self):
        # type: () -> None
        """
        Removes the decider conditions. This includes the condition itself, as
        well as the ``"copy_count_from_input"`` key.
        """
        self.control_behavior.pop("decider_conditions", None)
