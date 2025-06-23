# arithmetic_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ArithmeticOperation,
    CircuitNetworkSelection,
    SignalID,
    int32,
)
from draftsman.utils import reissue_warnings, fix_incorrect_pre_init
from draftsman.validators import and_, conditional, instance_of, one_of, try_convert
from draftsman.warning import PureVirtualDisallowedWarning, SignalConfigurationWarning

from draftsman.data.entities import arithmetic_combinators

import attrs
from typing import Literal, Optional, Union
import warnings


@conditional(ValidationMode.STRICT)
def _ensure_valid_virtual_signal(self, attr, value):
    if isinstance(value, SignalID) and value.name in {
        "signal-anything",
        "signal-everything",
    }:
        msg = "signal '{}' is not allowed anywhere in an arithmetic combinator".format(
            value.name
        )
        warnings.warn(PureVirtualDisallowedWarning(msg))


@conditional(ValidationMode.STRICT)
def _ensure_proper_each_configuration(
    self, attr, value, mode=None, warning_list: Optional[list] = None
):
    # TODO: ensure this is only called on validation of the entire
    # thing

    # Ensure that if the output signal is set to "signal-each",
    # one of the input signals must also be "signal-each"
    # TODO: write this better
    each_in_inputs = False
    if (
        isinstance(self.first_operand, SignalID)
        and self.first_operand.name == "signal-each"
    ):
        each_in_inputs = True
    elif (
        isinstance(self.second_operand, SignalID)
        and self.second_operand.name == "signal-each"
    ):
        each_in_inputs = True

    if value is not None and value.name == "signal-each" and not each_in_inputs:
        msg = "Cannot set the output signal to 'signal-each' when neither of the input signals are 'signal-each'"
        warnings.warn(SignalConfigurationWarning(msg))


@fix_incorrect_pre_init
@attrs.define
class ArithmeticCombinator(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An arithmetic combinator. Peforms a mathematical or bitwise operation on
    circuit signals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return arithmetic_combinators

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    first_operand: Union[SignalID, int32, None] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=and_(
            instance_of(Union[SignalID, int32, None]), _ensure_valid_virtual_signal
        ),
    )
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

    :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
        ``str`` name of a valid signal, an ``int``, or ``None``.
    :exception DraftsmanError: If set to ``"signal-anything"`` or
        ``"signal-everything"``.
    :exception DraftsmanError: If set to ``"signal-each"`` when
        :py:attr:`.second_operand` is also set to ``"signal-each"``.
    """

    # =========================================================================

    first_operand_wires: CircuitNetworkSelection = attrs.field(
        factory=CircuitNetworkSelection,
        converter=CircuitNetworkSelection.converter,
        validator=instance_of(CircuitNetworkSelection),
    )
    """
    TODO

    .. NOTE::

        In Factorio 1.0, inputs always utilize both wires regardless of this 
        value, and this value is stripped when exporting to that version.
    """

    # =========================================================================

    operation: ArithmeticOperation = attrs.field(
        default="*",
        converter=try_convert(str.upper),
        validator=one_of(ArithmeticOperation),
    )
    """
    The operation of the ``ArithmeticCombinator`` Can be one of:

    .. code-block:: python

        ["*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"]

    or ``None``. If the letter operations are specified as lowercase, they
    are automatically converted to uppercase on set.

    :getter: Gets the current operation, or ``None`` if not set.
    :setter: Sets the current operation. Removes the key if set to ``None``.

    :exception TypeError: If set to anything other than one of the values
        specified above.
    """

    # =========================================================================

    second_operand: Union[SignalID, int32, None] = attrs.field(
        default=0,
        converter=SignalID.converter,
        validator=and_(
            instance_of(Union[SignalID, int32, None]), _ensure_valid_virtual_signal
        ),
    )
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

    :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
        ``str`` name of a valid signal, an ``int``, or ``None``.
    :exception DraftsmanError: If set to ``"signal-anything"`` or
        ``"signal-everything"``.
    :exception DraftsmanError: If set to ``"signal-each"`` when
        :py:attr:`.first_operand` is also set to ``"signal-each"``.
    """

    # =========================================================================

    second_operand_wires: CircuitNetworkSelection = attrs.field(
        factory=CircuitNetworkSelection,
        converter=CircuitNetworkSelection.converter,
        validator=instance_of(CircuitNetworkSelection),
    )
    """
    TODO
    """

    # =========================================================================

    output_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=and_(
            instance_of(Optional[SignalID]),
            _ensure_valid_virtual_signal,
            _ensure_proper_each_configuration,
        ),
    )
    """
    The output signal of the ``ArithmeticCombinator``. Cannot be set to
    ``"signal-anything"`` or ``"signal-everything"`` as those signals are
    prohibited on combinators of this type. Can be set to ``"signal-each"``,
    but only if one of :py:attr:`.first_operand` or :py:attr:`.second_operand`
    are set to ``"signal-each"`` as well.

    :getter: Gets the output signal, or ``None`` if not set.
    :setter: Sets the output signal. Removes the key if set to ``None``.

    :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
        ``None``.
    :exception InvalidSignalError: If set to ``"signal-anything"`` or
        ``"signal-everything"``.
    :exception DraftsmanError: If set to ``"signal-each"`` when neither
        :py:attr:`.first_operand` nor :py:attr:`.second_operand` is set to
        ``"signal-each"``.
    """

    # =========================================================================

    @reissue_warnings
    def set_arithmetic_conditions(
        self,
        first_operand: Union[str, SignalID, int32, None] = None,
        first_operand_wires: set[Literal["red", "green"]] = {"red", "green"},
        operation: ArithmeticOperation = "*",
        second_operand: Union[str, SignalID, int32, None] = 0,
        second_operand_wires: set[Literal["red", "green"]] = {"red", "green"},
        output_signal: Union[str, SignalID, None] = None,
    ):
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

        self.first_operand = first_operand
        self.first_operand_wires = first_operand_wires
        self.operation = operation
        self.second_operand = second_operand
        self.second_operand_wires = second_operand_wires
        self.output_signal = output_signal

    # =========================================================================

    def merge(self, other: "ArithmeticCombinator"):
        super().merge(other)

        self.first_operand = other.first_operand
        self.first_operand_wires = other.first_operand_wires
        self.operation = other.operation
        self.second_operand = other.second_operand
        self.second_operand_wires = other.second_operand_wires
        self.output_signal = other.output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


@attrs.define
class _ExportArithmeticConditions:
    first_signal: Optional[SignalID] = None
    first_constant: Optional[int32] = None
    second_signal: Optional[SignalID] = None
    second_constant: Optional[int32] = 0


_export_fields = attrs.fields(_ExportArithmeticConditions)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    ArithmeticCombinator,
    lambda fields: {
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_constant",
        ): fields.first_operand.name,  # Happens first
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_signal",
        ): fields.first_operand.name,  # Overwrites if found
        # None: fields.first_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "operation",
        ): fields.operation.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_constant",
        ): fields.second_operand.name,  # Happens first
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_signal",
        ): fields.second_operand.name,  # Overwrites if found
        # None: fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
    lambda fields, converter: {
        ("control_behavior", "arithmetic_conditions", "first_constant",): (
            _export_fields.first_constant,
            lambda inst: inst.first_operand
            if isinstance(inst.first_operand, int)
            else None,
        ),
        ("control_behavior", "arithmetic_conditions", "first_signal",): (
            _export_fields.first_signal,
            lambda inst: converter.unstructure(inst.first_operand)
            if not isinstance(inst.first_operand, int)
            else None,
        ),
        # None: fields.first_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "operation",
        ): fields.operation.name,
        ("control_behavior", "arithmetic_conditions", "second_constant",): (
            _export_fields.second_constant,
            lambda inst: inst.second_operand
            if isinstance(inst.second_operand, int)
            else None,
        ),
        ("control_behavior", "arithmetic_conditions", "second_signal_signal",): (
            _export_fields.second_signal,
            lambda inst: converter.unstructure(inst.second_operand)
            if not isinstance(inst.second_operand, int)
            else None,
        ),
        # None: fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
)


draftsman_converters.get_version((2, 0)).add_hook_fns(
    ArithmeticCombinator,
    lambda fields: {
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_constant",
        ): fields.first_operand.name,  # Happens first
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_signal",
        ): fields.first_operand.name,  # Overwrites first_constant if found
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_signal_networks",
        ): fields.first_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "operation",
        ): fields.operation.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_constant",
        ): fields.second_operand.name,  # Happens first
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_signal",
        ): fields.second_operand.name,  # Overwrites second_constant if found
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_signal_networks",
        ): fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
    lambda fields, converter: {
        ("control_behavior", "arithmetic_conditions", "first_constant",): (
            _export_fields.first_constant,
            lambda inst: converter.unstructure(inst.first_operand)
            if isinstance(inst.first_operand, int)
            else None,
        ),
        ("control_behavior", "arithmetic_conditions", "first_signal",): (
            _export_fields.first_signal,
            lambda inst: converter.unstructure(inst.first_operand)
            if not isinstance(inst.first_operand, int)
            else None,
        ),
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_signal_networks",
        ): fields.first_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "operation",
        ): fields.operation.name,
        ("control_behavior", "arithmetic_conditions", "second_constant",): (
            _export_fields.second_constant,
            lambda inst: converter.unstructure(inst.second_operand)
            if isinstance(inst.second_operand, int)
            else None,
        ),
        ("control_behavior", "arithmetic_conditions", "second_signal",): (
            _export_fields.second_signal,
            lambda inst: converter.unstructure(inst.second_operand)
            if not isinstance(inst.second_operand, int)
            else None,
        ),
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_signal_networks",
        ): fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
)
