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
from draftsman.error import DataFormatError, InvalidSignalError, DraftsmanError
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import arithmetic_combinators
from draftsman import utils

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
        The first operand of the ``ArithmeticCombinator``. Cannot be set to
        ``"signal-anything"`` or ``"signal-everything"`` as those signals are
        prohibited on combinators of this type. Raises an error if set to
        ``"signal-each"`` while the second operand is also ``"signal-each"``, as
        only one of the two can be that signal at the same time. If the
        :py:attr:`.output_signal` of this combinator is set to ``"signal-each"``
        and this operand is *unset* from ``"signal-each"``, the output signal is
        set to ``None``.

        :getter: Gets the first operand of the operation, or ``None`` if not set.
        :setter: Sets the first operand of the operation. Removes the key if set
            to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
            ``str`` name of a valid signal, an ``int``, or ``None``.
        :exception DraftsmanError: If set to ``"signal-anything"`` or
            ``"signal-everything"``.
        :exception DraftsmanError: If set to ``"signal-each"`` when
            :py:attr:`.second_operand` is also set to ``"signal-each"``.
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

        old_value = self.first_operand

        if value is None:  # Default
            arithmetic_conditions.pop("first_signal", None)
            arithmetic_conditions.pop("first_constant", None)
        elif isinstance(value, dict):  # Signal Dict
            # Make sure the signals are not anything or everything
            if value["name"] in {"signal-anything", "signal-everything"}:
                raise DraftsmanError(
                    "Signal '{}' is not allowed in ArithmeticCombinator".format(
                        value["name"]
                    )
                )

            # Make sure both operands are not signal-each
            if isinstance(self.second_operand, dict):
                second_operand_name = self.second_operand["name"]
            else:
                second_operand_name = None

            if value["name"] == "signal-each" and second_operand_name == "signal-each":
                raise DraftsmanError(
                    "Both operands cannot be set to 'signal-each' simultaneously"
                )

            arithmetic_conditions["first_signal"] = value
            arithmetic_conditions.pop("first_constant", None)
        else:  # Constant
            arithmetic_conditions["first_constant"] = value
            arithmetic_conditions.pop("first_signal", None)

        # If the operand was 'signal-each' and we changed it to something else,
        # delete the output signal if it was also 'signal-each'
        if (
            isinstance(old_value, dict)
            and old_value["name"] == "signal-each"
            and isinstance(value, dict)
            and value["name"] != "signal-each"
            and self.output_signal is not None
            and self.output_signal["name"] == "signal-each"
        ):
            warnings.warn(
                "first_operand unset from 'signal-each'; output_signal can no "
                "longer be 'signal-each' and will be reset to `None`",
                DraftsmanWarning,
                stacklevel=2,
            )
            self.output_signal = None

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
        The second operand of the ``ArithmeticCombinator``. Cannot be set to
        ``"signal-anything"`` or ``"signal-everything"`` as those signals are
        prohibited on combinators of this type. Raises an error if set to
        ``"signal-each"`` while the first operand is also ``"signal-each"``, as
        only one of the two can be that signal at the same time. If the
        :py:attr:`.output_signal` of this combinator is set to ``"signal-each"``
        and this operand is *unset* from ``"signal-each"``, the output signal is
        set to ``None``.

        :getter: Gets the second operand of the operation, or ``None`` if not
            set.
        :setter: Sets the second operand of the operation. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
            ``str`` name of a valid signal, an ``int``, or ``None``.
        :exception DraftsmanError: If set to ``"signal-anything"`` or
            ``"signal-everything"``.
        :exception DraftsmanError: If set to ``"signal-each"`` when
            :py:attr:`.first_operand` is also set to ``"signal-each"``.
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

        old_value = self.second_operand

        if value is None:  # Default
            arithmetic_conditions.pop("second_signal", None)
            arithmetic_conditions.pop("second_constant", None)
        elif isinstance(value, dict):  # Signal Dict
            # Make sure the signals are not anything or everything
            if value["name"] in {"signal-anything", "signal-everything"}:
                raise DraftsmanError(
                    "Signal '{}' is not allowed in ArithmeticCombinator".format(
                        value["name"]
                    )
                )

            # Make sure both operands are not signal-each
            if isinstance(self.first_operand, dict):
                first_operand_name = self.first_operand["name"]
            else:
                first_operand_name = None

            if value["name"] == "signal-each" and first_operand_name == "signal-each":
                raise DraftsmanError(
                    "Both operands cannot be set to 'signal-each' simultaneously"
                )

            arithmetic_conditions["second_signal"] = value
            arithmetic_conditions.pop("second_constant", None)
        else:  # Constant
            arithmetic_conditions["second_constant"] = value
            arithmetic_conditions.pop("second_signal", None)

        # If the operand was 'signal-each' and we changed it to something else,
        # delete the output signal if it was also 'signal-each'
        if (
            isinstance(old_value, dict)
            and old_value["name"] == "signal-each"
            and isinstance(value, dict)
            and value["name"] != "signal-each"
            and self.output_signal is not None
            and self.output_signal["name"] == "signal-each"
        ):
            warnings.warn(
                "second_operand unset from 'signal-each'; output_signal can no "
                "longer be 'signal-each' and will be reset to `None`",
                DraftsmanWarning,
                stacklevel=2,
            )
            self.output_signal = None

    # =========================================================================

    @property
    def output_signal(self):
        # type: () -> dict
        """
        The output signal of the ``ArithmeticCombinator``. Cannot be set to
        ``"signal-anything"`` or ``"signal-everything"`` as those signals are
        prohibited on combinators of this type. Can be set to ``"signal-each"``,
        but only if one of :py:attr:`.first_operand` or :py:attr:`.second_operand`
        are set to ``"signal-each"`` as well.

        :getter: Gets the output signal, or ``None`` if not set.
        :setter: Sets the output signal. Removes the key if set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
            ``None``.
        :exception InvalidSignalError: If set to ``"signal-anything"`` or
            ``"signal-everything"``.
        :exception DraftsmanError: If set to ``"signal-each"`` when neither
            :py:attr:`.first_operand` nor :py:attr:`.second_operand` is set to
            ``"signal-each"``.
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
            # Make sure the signals are not anything or everything
            if value["name"] in {"signal-anything", "signal-everything"}:
                raise InvalidSignalError(
                    "Signal '{}' is not allowed in ArithmeticCombinator".format(
                        value["name"]
                    )
                )

            # Make sure if the signal is "signal-each" that one of the operands
            # are also signal each
            if isinstance(self.first_operand, dict):
                first_operand_name = self.first_operand["name"]
            else:
                first_operand_name = None

            if isinstance(self.second_operand, dict):
                second_operand_name = self.second_operand["name"]
            else:
                second_operand_name = None

            if (
                value["name"] == "signal-each"
                and first_operand_name != "signal-each"
                and second_operand_name != "signal-each"
            ):
                raise DraftsmanError(
                    "Cannot set 'output_signal' to 'signal-each' when neither "
                    "first nor second operands are 'signal-each'"
                )

            arithmetic_conditions["output_signal"] = value

    # =========================================================================

    @utils.reissue_warnings
    def set_arithmetic_conditions(
        self, first_operand=None, operation="*", second_operand=0, output_signal=None
    ):
        # type: (Union[str, int], str, Union[str, int], str) -> None
        """
        Sets the entire arithmetic condition of the ``ArithmeticCombinator`` all
        at once. All of the restrictions for each individual attribute apply.

        :param first_operand: The name of the first signal to set, some constant,
            or ``None``.
        :param operation: The string representation of the operation to perform.
            See :py:data:`.OPERATION` for more information on valid values.
        :param second_operand: The name of the second signal to set, some
            constant, or ``None``.
        :param output_signal: The name of the output signal to set, or ``None``.

        :exception DataFormatError: If any argument fails to match the formats
            specified above.
        """

        # Check all the parameters before we set anything to preserve original
        try:
            first_operand = signatures.SIGNAL_ID_OR_CONSTANT.validate(first_operand)
            operation = signatures.OPERATION.validate(operation)
            second_operand = signatures.SIGNAL_ID_OR_CONSTANT.validate(second_operand)
            output_signal = signatures.SIGNAL_ID_OR_NONE.validate(output_signal)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        self.first_operand = first_operand
        self.operation = operation
        self.second_operand = second_operand
        self.output_signal = output_signal

    def remove_arithmetic_conditions(self):
        # type: () -> None
        """
        Removes the entire ``"arithmetic_conditions"`` key from the control
        behavior. This is used to quickly delete the entire condition, and to
        tidy up cases where all of the other attributes are set to ``None``, but
        the ``"arithmetic_conditions"`` dictionary still exists, taking up space
        in the exported string.
        """
        self.control_behavior.pop("arithmetic_conditions", None)
