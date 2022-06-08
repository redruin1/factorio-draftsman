# decider_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.error import DataFormatError, DraftsmanError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import decider_combinators
from draftsman.data import signals
from draftsman import utils

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

        # Matrix of values, where keys are the name of the first_operand and
        # the values are sets of signals that cannot be set as output_signal
        self.signal_blacklist = {
            "signal-everything": {"signal-anything", "signal-each"},
            "signal-anything": {"signal-each"},
            "signal-each": {"signal-everything", "signal-anything"},
        }

    # =========================================================================

    @property
    def first_operand(self):
        # type: () -> Union[str, int]
        """
        The first operand of the ``DeciderCombinator``. Must be a signal or ``None``;
        cannot be a constant. Has a number of restrictions on which of the
        "special" signals can be in this position in relation to
        :py:attr:`.output_signal`:

        .. list-table::
            :header-rows: 1

            * - ``first_operand`` value
              - Valid ``output_signal`` value(s)
            * - All Normal Signals
              - | All Normal Signals,
                | ``"signal-everything"``
            * - ``"signal-everything"``
              - | All Normal Signals,
                | ``"signal-everything"``
            * - ``"signal-anything"``
              - | All Normal Signals,
                | ``"signal-everything"``,
                | ``"signal-anything"``
            * - ``"signal-each"``
              - | All Normal Signals,
                | ``"signal-each"``

        If ``first_operand`` is set to something that makes ``output_signal``
        fall outside of these accepted values, then ``output_signal`` is reset
        to ``None``.

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

        # If the signal blacklist of the new first operand conflicts with the
        # current 'output_signal', we remove it
        if isinstance(self.output_signal, dict):
            output_signal_name = self.output_signal["name"]
        else:
            output_signal_name = None

        if isinstance(value, dict):
            value_name = value["name"]
        else:
            value_name = None

        current_blacklist = self.signal_blacklist.get(
            value_name, {"signal-anything", "signal-each"}
        )
        if output_signal_name in current_blacklist:
            warnings.warn(
                "'{}' cannot be an output_signal when '{}' is the first operand; "
                "output_signal will be set to `None`".format(
                    output_signal_name, value_name
                ),
                DraftsmanWarning,
                stacklevel=2,
            )
            self.output_signal = None

    # =========================================================================

    @property
    def operation(self):
        # type: () -> str
        """
        The operation of the ``DeciderCombinator`` Can be specified as the
        single unicode character which is used by Factorio, or you can use the
        Python formatted 2-character equivalents::

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

        return decider_conditions.get("comparator", None)

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
            decider_conditions.pop("comparator", None)
        else:
            decider_conditions["comparator"] = value

    # =========================================================================

    @property
    def second_operand(self):
        # type: () -> Union[dict, int]
        """
        The second operand of the ``DeciderCombinator``. Cannot be one of the
        :py:data:`.pure_virtual` signals, which is forbidden for this operand in
        combinators of this type.

        :getter: Gets the second operand of the operation, or ``None`` if not
            set.
        :setter: Sets the second operand of the operation. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID_OR_CONSTANT`

        :exception TypeError: If set to anything other than a ``SIGNAL_ID``, an
            ``int``, or ``None``.
        :exception DraftsmanError: If set to a pure virtual signal, which is
            forbidden.
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
            # Make sure second operand was not set to a fancy signal
            if value["name"] in signals.pure_virtual:
                raise DraftsmanError(
                    "'second_operand' cannot be set to pure virtual signal '{}'".format(
                        value["name"]
                    )
                )

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
        :exception DraftsmanError: If set to a value which conflicts with
            :py:attr:`.first_operand`; see that attribute for more information.
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
            # Check the first operand and determine it's blacklisted signals;
            # ensure the value we're setting 'output_signal' to is not in that
            # blacklist
            if isinstance(self.first_operand, dict):
                first_operand_name = self.first_operand["name"]
            else:
                first_operand_name = None

            current_blacklist = self.signal_blacklist.get(
                first_operand_name, {"signal-anything", "signal-each"}
            )
            if value["name"] in current_blacklist:
                raise DraftsmanError(
                    "Cannot set 'output_signal' to '{}'; it must be in {}".format(
                        value["name"], current_blacklist
                    )
                )
            decider_conditions["output_signal"] = value

    # =========================================================================

    @property
    def copy_count_from_input(self):
        # type: () -> bool
        """
        Whether or not the input value of a signal is transposed to the output
        signal. If this is false, the output signal is output with a value of 1
        if the condition is met. A default of ``None`` means ``True``.

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

    @utils.reissue_warnings
    def set_decider_conditions(
        self,
        first_operand=None,
        operation="<",
        second_operand=0,
        output_signal=None,
        copy_count_from_input=None,
    ):
        # type: (Union[str, int], str, Union[str, int], str, bool) -> None
        """
        Set the operation for the ``DeciderCombinator`` all at once. All of the
        restrictions to the individual attributes apply.

        :param first_operand: The name of the first signal to set, or ``None``.
        :param operation: The comparison operator to use. See :py:data:`.COMPARATOR`
            for more information on valid values.
        :param second_operand: The name of the second signal, some constant, or
            ``None``.
        :param output_signal: The name of the output signal to set, or ``None``.
        :param copy_count_from_input: Whether or not to copy input signal values
            to output signal values. Defaults to ``None``, which also means ``True``.

        :exception DataFormatError: If the any of the arguments fail to match
            their correct formats.
        """
        # Check all the parameters before we set anything to preserve original
        try:
            first_operand = signatures.SIGNAL_ID_OR_NONE.validate(first_operand)
            operation = signatures.COMPARATOR.validate(operation)
            second_operand = signatures.SIGNAL_ID_OR_CONSTANT.validate(second_operand)
            output_signal = signatures.SIGNAL_ID_OR_NONE.validate(output_signal)
            copy_count_from_input = signatures.BOOL_OR_NONE.validate(
                copy_count_from_input
            )
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        self.first_operand = first_operand
        self.operation = operation
        self.second_operand = second_operand
        self.output_signal = output_signal
        self.copy_count_from_input = copy_count_from_input

    def remove_decider_conditions(self):
        # type: () -> None
        """
        Removes the entire ``"decider_conditions"`` key from the control
        behavior. This is used to quickly delete the entire condition, and to
        tidy up cases where all of the other attributes are set to ``None``, but
        the ``"decider_conditions"`` dictionary still exists, taking up space
        in the exported string.
        """
        self.control_behavior.pop("decider_conditions", None)
