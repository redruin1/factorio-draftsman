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

    # @property
    # def first_operand(self):
    #     # type: () -> Union[str, int]
    #     """
    #     TODO
    #     """
    #     decider_conditions = self.control_behavior.get("decider_conditions", None)
    #     if not decider_conditions:
    #         return None

    #     if "first_signal" in decider_conditions:
    #         return decider_conditions["first_signal"]
    #     elif "first_constant" in decider_conditions:
    #         return decider_conditions["first_constant"]
    #     elif "second_signal" in decider_conditions: # Check constant
    #         return decider_conditions.get("constant", None)

    #     return None

    # @first_operand.setter
    # def first_operand(self, value):
    #     # type: (Union[dict, int]) -> None
    #     try:
    #         value = signatures.SIGNAL_ID_OR_CONSTANT.validate(value)
    #     except SchemaError:
    #         # TODO: more verbose
    #         raise TypeError("Invalid first_operand format")

    #     if "decider_conditions" not in self.control_behavior:
    #         self.control_behavior["decider_conditions"] = {}
    #     decider_conditions = self.control_behavior["decider_conditions"]

    #     if value is None: # Default
    #         decider_conditions.pop("first_signal", None)
    #         decider_conditions.pop("first_constant", None)
    #         if ("constant" in decider_conditions and
    #             "second_signal" in decider_conditions):
    #             decider_conditions.pop("constant", None)
    #     elif isinstance(value, dict): # Signal Dict
    #         decider_conditions["first_signal"] = value
    #         decider_conditions.pop("first_constant", None)
    #         if ("constant" in decider_conditions and
    #             "second_signal" in decider_conditions):
    #             decider_conditions.pop("constant", None)
    #     else: # Constant
    #         decider_conditions.pop("first_signal", None)
    #         if ("constant" in decider_conditions and
    #             "second_signal" not in decider_conditions):
    #             old_constant = decider_conditions.pop("constant")
    #             decider_conditions["second_constant"] = old_constant
    #             decider_conditions["first_constant"] = value
    #         else:
    #             decider_conditions["constant"] = value

    # =========================================================================

    # @property
    # def operation(self):
    #     # type: () -> str
    #     """
    #     TODO
    #     """
    #     decider_conditions = self.control_behavior.get("decider_conditions", None)
    #     if not decider_conditions:
    #         return None

    #     return decider_conditions.get("operation", None)

    # @operation.setter
    # def operation(self, value):
    #     # type: (str) -> None
    #     try:
    #         value = signatures.OPERATION.validate(value)
    #     except SchemaError:
    #         # TODO: more verbose
    #         raise TypeError("Invalid first_operand format")

    #     if "decider_conditions" not in self.control_behavior:
    #         self.control_behavior["decider_conditions"] = {}
    #     decider_conditions = self.control_behavior["decider_conditions"]

    #     if value is None:
    #         decider_conditions.pop("operation", None)
    #     else:
    #         decider_conditions["operation"] = value

    # =========================================================================

    # @property
    # def second_operand(self):
    #     # type: () -> Union[dict, int]
    #     """
    #     TODO
    #     """
    #     decider_conditions = self.control_behavior.get("decider_conditions", None)
    #     if not decider_conditions:
    #         return None

    #     if "second_signal" in decider_conditions:
    #         return decider_conditions["second_signal"]
    #     elif "second_constant" in decider_conditions:
    #         return decider_conditions["second_constant"]
    #     elif "first_signal" in decider_conditions: # Check constant
    #         return decider_conditions.get("constant", None)

    #     return None

    # @second_operand.setter
    # def second_operand(self, value):
    #     # type: (Union[str, int]) -> None
    #     try:
    #         value = signatures.SIGNAL_ID_OR_CONSTANT.validate(value)
    #     except SchemaError:
    #         # TODO: more verbose
    #         raise TypeError("Invalid first_operand format")

    #     if "decider_conditions" not in self.control_behavior:
    #         self.control_behavior["decider_conditions"] = {}
    #     decider_conditions = self.control_behavior["decider_conditions"]

    #     if value is None: # Default
    #         decider_conditions.pop("second_signal", None)
    #         decider_conditions.pop("second_constant", None)
    #         if ("constant" in decider_conditions and
    #             "first_signal" in decider_conditions):
    #             decider_conditions.pop("constant", None)
    #     elif isinstance(value, dict): # Signal Dict
    #         decider_conditions["second_signal"] = value
    #         decider_conditions.pop("second_constant", None)
    #         if ("constant" in decider_conditions and
    #             "first_signal" in decider_conditions):
    #             decider_conditions.pop("constant", None)
    #     else: # Constant
    #         decider_conditions.pop("second_signal", None)
    #         if ("constant" in decider_conditions and
    #             "first_signal" not in decider_conditions):
    #             old_constant = decider_conditions.pop("constant")
    #             decider_conditions["first_constant"] = old_constant
    #             decider_conditions["second_constant"] = value
    #         else:
    #             decider_conditions["constant"] = value

    # =========================================================================

    # @property
    # def output_signal(self):
    #     # type: () -> dict
    #     """
    #     TODO
    #     """
    #     decider_conditions = self.control_behavior.get("decider_conditions", None)
    #     if not decider_conditions:
    #         return None

    #     return decider_conditions.get("output_signal", None)

    # @output_signal.setter
    # def output_signal(self, value):
    #     # type: (str) -> None
    #     try:
    #         out = signatures.SIGNAL_ID.validate(out)
    #     except SchemaError:
    #         # TODO: more verbose
    #         raise TypeError("Invalid output_signal format")

    #     if "decider_conditions" not in self.control_behavior:
    #         self.control_behavior["decider_conditions"] = {}
    #     decider_conditions = self.control_behavior["decider_conditions"]

    #     if out is None: # Default
    #         decider_conditions.pop("output_signal", None)
    #     else: # Signal Dict
    #         decider_conditions["output_signal"] = out

    # =========================================================================

    @property
    def copy_count_from_input(self):
        # type: () -> bool
        """
        Whether or not the input value of a signal is transposed to the output
        signal.

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

        :param a: The first signal, constant, or ``None``, as specified in
            :py:data:`.SIGNAL_ID_OR_CONSTANT`.
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
            a = signatures.SIGNAL_ID_OR_CONSTANT.validate(a)
            cmp = signatures.COMPARATOR.validate(cmp)
            b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
            out = signatures.SIGNAL_ID_OR_NONE.validate(out)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        double_constant = isinstance(a, int) and isinstance(b, int)
        a_not_const = not isinstance(a, int)
        b_not_const = isinstance(b, int)

        # A
        if a is None:  # Default
            decider_conditions.pop("first_signal", None)
            decider_conditions.pop("first_constant", None)
            if not double_constant and b_not_const:
                decider_conditions.pop("constant", None)
        elif isinstance(a, dict):  # Signal Dict
            decider_conditions["first_signal"] = a
            decider_conditions.pop("first_constant", None)
        else:  # Constant
            decider_conditions.pop("first_signal", None)
            if double_constant:
                decider_conditions["first_constant"] = a
                decider_conditions.pop("constant", None)
            else:
                decider_conditions["constant"] = a
                decider_conditions.pop("first_constant", None)

        # op
        if cmp is None:
            decider_conditions.pop("comparator", None)
        else:
            decider_conditions["comparator"] = cmp

        # B
        if b is None:  # Default
            decider_conditions.pop("second_signal", None)
            decider_conditions.pop("second_constant", None)
            if not double_constant and a_not_const:
                decider_conditions.pop("constant", None)
        elif isinstance(b, dict):  # Signal Dict
            decider_conditions["second_signal"] = b
            decider_conditions.pop("second_constant", None)
        else:  # Constant
            decider_conditions.pop("second_signal", None)
            if double_constant:
                decider_conditions["second_constant"] = b
                decider_conditions.pop("constant", None)
            else:
                decider_conditions["constant"] = b
                decider_conditions.pop("second_constant", None)

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
        # TODO: delete this function
        self.control_behavior.pop("decider_conditions", None)
