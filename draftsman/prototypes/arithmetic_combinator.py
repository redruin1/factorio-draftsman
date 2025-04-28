# arithmetic_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ArithmeticOperation,
    DraftsmanBaseModel,
    NetworkSpecification,
    AttrsNetworkSpecification,
    AttrsSignalID,
    SignalID,
    int32,
)
from draftsman.utils import get_first, reissue_warnings, fix_incorrect_pre_init
from draftsman.validators import and_, instance_of, one_of, try_convert
from draftsman.warning import PureVirtualDisallowedWarning, SignalConfigurationWarning

from draftsman.data.entities import arithmetic_combinators

import attrs
from pydantic import ConfigDict, Field, ValidationInfo, field_validator, model_validator
from typing import Any, Literal, Optional, Union
from typing_extensions import TypedDict
import warnings


def _ensure_valid_virtual_signal(self, attr, value, mode=None):
    mode = mode if mode is not None else self.validate_assignment

    if mode >= ValidationMode.STRICT:
        if isinstance(value, AttrsSignalID) and value.name in {
            "signal-anything",
            "signal-everything",
        }:
            msg = "signal '{}' is not allowed anywhere in an arithmetic combinator".format(
                value.name
            )
            warnings.warn(PureVirtualDisallowedWarning(msg))


def _ensure_proper_each_configuration(self, attr, value, mode=None):
    mode = mode if mode is not None else self.validate_assignment

    if mode >= ValidationMode.STRICT:

        # TODO: ensure this is only called on validation of the entire
        # thing

        # Ensure that if the output signal is set to "signal-each",
        # one of the input signals must also be "signal-each"
        # TODO: write this better
        each_in_inputs = False
        if (
            isinstance(self.first_operand, AttrsSignalID)
            and self.first_operand.name == "signal-each"
        ):
            each_in_inputs = True
        elif (
            isinstance(self.second_operand, AttrsSignalID)
            and self.second_operand.name == "signal-each"
        ):
            each_in_inputs = True

        if value is not None and value.name == "signal-each" and not each_in_inputs:
            msg = "Cannot set the output signal to 'signal-each' when neither of the input signals are 'signal-each'"
            warnings.warn(SignalConfigurationWarning(msg))

    return self


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

    # class Format(
    #     PlayerDescriptionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         class ArithmeticConditions(DraftsmanBaseModel):
    #             first_constant: Optional[int32] = Field(
    #                 None,
    #                 description="""
    #                 The constant value located in the left slot, if present.
    #                 """,
    #             )
    #             first_signal: Optional[SignalID] = Field(
    #                 None,
    #                 description="""
    #                 The signal type located in the left slot, if present. If
    #                 both this key and 'first_constant' are defined, this key
    #                 takes precedence.
    #                 """,
    #             )
    #             first_signal_networks: Optional[NetworkSpecification] = Field(
    #                 NetworkSpecification(),
    #                 description="""
    #                 Which input wire networks to pull from when evaluating the
    #                 value of the first signal.
    #                 """,
    #             )
    #             operation: Literal[
    #                 "*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None
    #             ] = Field(
    #                 "*",
    #                 description="""
    #                 The operation to perform on the two operands.
    #                 """,
    #             )
    #             second_constant: Optional[int32] = Field(
    #                 0,
    #                 description="""
    #                 The constant value located in the right slot, if present.
    #                 """,
    #             )
    #             second_signal: Optional[SignalID] = Field(
    #                 None,
    #                 description="""
    #                 The signal type located in the right slot, if present. If
    #                 both this key and 'second_constant' are defined, this key
    #                 takes precedence.
    #                 """,
    #             )
    #             second_signal_networks: Optional[NetworkSpecification] = Field(
    #                 NetworkSpecification(),
    #                 description="""
    #                 Which input wire networks to pull from when evaluating the
    #                 value of the second signal.
    #                 """,
    #             )
    #             output_signal: Optional[SignalID] = Field(
    #                 None,
    #                 description="""
    #                 The output signal to emit the operation result as. Can be
    #                 'signal-each', but only if one of 'first_signal' or
    #                 'second_signal' is also 'signal-each'. No other pure virtual
    #                 signals are permitted in arithmetic combinators.
    #                 """,
    #             )

    #             @field_validator("operation", mode="before")
    #             @classmethod
    #             def ensure_upper(cls, value: Optional[str]):
    #                 if isinstance(value, str):
    #                     return value.upper()
    #                 return value

    #             @model_validator(mode="after")
    #             def ensure_no_forbidden_signals(self, info: ValidationInfo):
    #                 if not info.context:
    #                     return self
    #                 if info.context["mode"] <= ValidationMode.MINIMUM:
    #                     return self

    #                 warning_list: list = info.context["warning_list"]

    #                 signals = [
    #                     self.first_signal,
    #                     self.second_signal,
    #                     self.output_signal,
    #                 ]
    #                 signals = [signal for signal in signals if signal is not None]
    #                 forbidden_virtual_signals = {"signal-anything", "signal-everything"}
    #                 for signal in signals:
    #                     if signal.name in forbidden_virtual_signals:
    #                         warning_list.append(
    #                             PureVirtualDisallowedWarning(
    #                                 "signal '{}' is not allowed anywhere in an arithmetic combinator".format(
    #                                     signal.name
    #                                 )
    #                             )
    #                         )
    #                         break

    #                 return self

    #             # @model_validator(mode="after") # 1.0
    #             # def prohibit_2_each_signals(self, info: ValidationInfo):
    #             #     if not info.context:
    #             #         return self
    #             #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #             #         return self

    #             #     # This check only applies to Factorio 1.X
    #             #     if info.context["environment_version"] >= (2, 0):
    #             #         return self

    #             #     warning_list: list = info.context["warning_list"]

    #             #     # Ensure that "signal-each" does not occupy both first and
    #             #     # second signal slots
    #             #     if self.first_signal is not None and self.second_signal is not None:
    #             #         if (
    #             #             self.first_signal.name == "signal-each"
    #             #             and self.second_signal.name == "signal-each"
    #             #         ):
    #             #             warning_list.append(
    #             #                 SignalConfigurationWarning(
    #             #                     "Cannot have 'signal-each' occupy both the first and second slots of an arithmetic combinator"
    #             #                 )
    #             #             )

    #             #     return self

    #             @model_validator(mode="after")
    #             def ensure_proper_each_configuration(self, info: ValidationInfo):
    #                 if not info.context:
    #                     return self
    #                 if info.context["mode"] <= ValidationMode.MINIMUM:
    #                     return self

    #                 warning_list: list = info.context["warning_list"]

    #                 # TODO: ensure this is only called on validation of the entire
    #                 # thing

    #                 # Ensure that if the output signal is set to "signal-each",
    #                 # one of the input signals must also be "signal-each"
    #                 # TODO: write this better
    #                 each_in_inputs = False
    #                 if (
    #                     self.first_signal is not None
    #                     and self.first_signal.name == "signal-each"
    #                 ):
    #                     each_in_inputs = True
    #                 elif (
    #                     self.second_signal is not None
    #                     and self.second_signal.name == "signal-each"
    #                 ):
    #                     each_in_inputs = True

    #                 if self.output_signal is not None:
    #                     if (
    #                         self.output_signal.name == "signal-each"
    #                         and not each_in_inputs
    #                     ):
    #                         warning_list.append(
    #                             SignalConfigurationWarning(
    #                                 "Cannot set the output signal to 'signal-each' when neither of the input signals are 'signal-each'"
    #                             )
    #                         )

    #                 return self

    #         arithmetic_conditions: Optional[
    #             ArithmeticConditions
    #         ] = ArithmeticConditions()

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="ArithmeticCombinator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(arithmetic_combinators),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Optional[Direction] = Direction.NORTH,
    #     player_description: Optional[str] = None,
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         arithmetic_combinators,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         player_description=player_description,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return arithmetic_combinators

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    first_operand: Union[AttrsSignalID, int32, None] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=and_(
            instance_of(Union[AttrsSignalID, int32, None]), _ensure_valid_virtual_signal
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

    # @property
    # def first_operand(self) -> Union[SignalID, int32, None]:
    #     """
    #     The first operand of the ``ArithmeticCombinator``. Cannot be set to
    #     ``"signal-anything"`` or ``"signal-everything"`` as those signals are
    #     prohibited on combinators of this type. Raises an error if set to
    #     ``"signal-each"`` while the second operand is also ``"signal-each"``, as
    #     only one of the two can be that signal at the same time. If the
    #     :py:attr:`.output_signal` of this combinator is set to ``"signal-each"``
    #     and this operand is *unset* from ``"signal-each"``, the output signal is
    #     set to ``None``.

    #     :getter: Gets the first operand of the operation, or ``None`` if not set.
    #     :setter: Sets the first operand of the operation. Removes the key if set
    #         to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
    #         ``str`` name of a valid signal, an ``int``, or ``None``.
    #     :exception DraftsmanError: If set to ``"signal-anything"`` or
    #         ``"signal-everything"``.
    #     :exception DraftsmanError: If set to ``"signal-each"`` when
    #         :py:attr:`.second_operand` is also set to ``"signal-each"``.
    #     """
    #     arithmetic_conditions = self.control_behavior.arithmetic_conditions
    #     if not arithmetic_conditions:
    #         return None

    #     if arithmetic_conditions.first_signal is not None:
    #         return arithmetic_conditions.first_signal
    #     elif arithmetic_conditions.first_constant is not None:
    #         return arithmetic_conditions.first_constant
    #     else:
    #         return None

    # @first_operand.setter
    # def first_operand(self, value: Union[str, SignalID, int32, None]):
    #     if self.control_behavior.arithmetic_conditions is None:
    #         self.control_behavior.arithmetic_conditions = (
    #             self.Format.ControlBehavior.ArithmeticConditions()
    #         )

    #     if value is None:  # Default
    #         self.control_behavior.arithmetic_conditions.first_signal = None
    #         self.control_behavior.arithmetic_conditions.first_constant = None
    #     elif isinstance(value, int):  # constant
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.ArithmeticConditions,
    #                 self.control_behavior.arithmetic_conditions,
    #                 "first_constant",
    #                 value,
    #             )
    #         self.control_behavior.arithmetic_conditions.first_constant = value
    #         self.control_behavior.arithmetic_conditions.first_signal = None
    #     else:  # other
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.ArithmeticConditions,
    #                 self.control_behavior.arithmetic_conditions,
    #                 "first_signal",
    #                 value,
    #             )
    #         self.control_behavior.arithmetic_conditions.first_signal = value
    #         self.control_behavior.arithmetic_conditions.first_constant = None

    # =========================================================================

    first_operand_wires: AttrsNetworkSpecification = attrs.field(
        factory=AttrsNetworkSpecification,
        converter=AttrsNetworkSpecification.converter,
        validator=instance_of(AttrsNetworkSpecification),
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

    # @property
    # def operation(
    #     self,
    # ) -> Literal["*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None]:
    #     """
    #     The operation of the ``ArithmeticCombinator`` Can be one of:

    #     .. code-block:: python

    #         ["*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"]

    #     or ``None``. If the letter operations are specified as lowercase, they
    #     are automatically converted to uppercase on set.

    #     :getter: Gets the current operation, or ``None`` if not set.
    #     :setter: Sets the current operation. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than one of the values
    #         specified above.
    #     """
    #     arithmetic_conditions = self.control_behavior.get("arithmetic_conditions", None)
    #     if not arithmetic_conditions:
    #         return None

    #     return self.control_behavior.arithmetic_conditions.operation

    # @operation.setter
    # def operation(
    #     self,
    #     value: Literal[
    #         "*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None
    #     ],
    # ):
    #     if self.control_behavior.arithmetic_conditions is None:
    #         self.control_behavior.arithmetic_conditions = (
    #             self.Format.ControlBehavior.ArithmeticConditions()
    #         )

    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.ArithmeticConditions,
    #             self.control_behavior.arithmetic_conditions,
    #             "operation",
    #             value,
    #         )
    #         self.control_behavior.arithmetic_conditions.operation = result
    #     else:
    #         self.control_behavior.arithmetic_conditions.operation = value

    # =========================================================================

    second_operand: Union[AttrsSignalID, int32, None] = attrs.field(
        default=0,
        converter=AttrsSignalID.converter,
        validator=and_(
            instance_of(Union[AttrsSignalID, int32, None]), _ensure_valid_virtual_signal
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

    # @property
    # def second_operand(self) -> Union[SignalID, int32, None]:
    #     """
    #     The second operand of the ``ArithmeticCombinator``. Cannot be set to
    #     ``"signal-anything"`` or ``"signal-everything"`` as those signals are
    #     prohibited on combinators of this type. Raises an error if set to
    #     ``"signal-each"`` while the first operand is also ``"signal-each"``, as
    #     only one of the two can be that signal at the same time. If the
    #     :py:attr:`.output_signal` of this combinator is set to ``"signal-each"``
    #     and this operand is *unset* from ``"signal-each"``, the output signal is
    #     set to ``None``.

    #     :getter: Gets the second operand of the operation, or ``None`` if not
    #         set.
    #     :setter: Sets the second operand of the operation. Removes the key if
    #         set to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID``, the
    #         ``str`` name of a valid signal, an ``int``, or ``None``.
    #     :exception DraftsmanError: If set to ``"signal-anything"`` or
    #         ``"signal-everything"``.
    #     :exception DraftsmanError: If set to ``"signal-each"`` when
    #         :py:attr:`.first_operand` is also set to ``"signal-each"``.
    #     """
    #     arithmetic_conditions = self.control_behavior.arithmetic_conditions
    #     if not arithmetic_conditions:
    #         return None

    #     if arithmetic_conditions.second_signal is not None:
    #         return arithmetic_conditions.second_signal
    #     elif arithmetic_conditions.second_constant is not None:
    #         return arithmetic_conditions.second_constant
    #     else:
    #         return None

    # @second_operand.setter
    # def second_operand(self, value: Union[str, SignalID, int32, None]):
    #     if self.control_behavior.arithmetic_conditions is None:
    #         self.control_behavior.arithmetic_conditions = (
    #             self.Format.ControlBehavior.ArithmeticConditions()
    #         )

    #     if value is None:  # Default
    #         self.control_behavior.arithmetic_conditions.second_signal = None
    #         self.control_behavior.arithmetic_conditions.second_constant = None
    #     elif isinstance(value, int):  # constant
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.ArithmeticConditions,
    #                 self.control_behavior.arithmetic_conditions,
    #                 "second_constant",
    #                 value,
    #             )
    #         self.control_behavior.arithmetic_conditions.second_constant = value
    #         self.control_behavior.arithmetic_conditions.second_signal = None
    #     else:  # other
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.ArithmeticConditions,
    #                 self.control_behavior.arithmetic_conditions,
    #                 "second_signal",
    #                 value,
    #             )
    #         self.control_behavior.arithmetic_conditions.second_signal = value
    #         self.control_behavior.arithmetic_conditions.second_constant = None

    # =========================================================================

    second_operand_wires: AttrsNetworkSpecification = attrs.field(
        factory=AttrsNetworkSpecification,
        converter=AttrsNetworkSpecification.converter,
        validator=instance_of(AttrsNetworkSpecification),
    )
    """
    TODO
    """

    # =========================================================================

    output_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=and_(
            instance_of(Optional[AttrsSignalID]),
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

    # @property
    # def output_signal(self) -> Optional[SignalID]:
    #     """
    #     The output signal of the ``ArithmeticCombinator``. Cannot be set to
    #     ``"signal-anything"`` or ``"signal-everything"`` as those signals are
    #     prohibited on combinators of this type. Can be set to ``"signal-each"``,
    #     but only if one of :py:attr:`.first_operand` or :py:attr:`.second_operand`
    #     are set to ``"signal-each"`` as well.

    #     :getter: Gets the output signal, or ``None`` if not set.
    #     :setter: Sets the output signal. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
    #         ``None``.
    #     :exception InvalidSignalError: If set to ``"signal-anything"`` or
    #         ``"signal-everything"``.
    #     :exception DraftsmanError: If set to ``"signal-each"`` when neither
    #         :py:attr:`.first_operand` nor :py:attr:`.second_operand` is set to
    #         ``"signal-each"``.
    #     """
    #     arithmetic_conditions = self.control_behavior.arithmetic_conditions
    #     if not arithmetic_conditions:
    #         return None

    #     return self.control_behavior.arithmetic_conditions.output_signal

    # @output_signal.setter
    # def output_signal(self, value: Union[str, SignalID, None]):
    #     if self.control_behavior.arithmetic_conditions is None:
    #         self.control_behavior.arithmetic_conditions = (
    #             self.Format.ControlBehavior.ArithmeticConditions()
    #         )

    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.ArithmeticConditions,
    #             self.control_behavior.arithmetic_conditions,
    #             "output_signal",
    #             value,
    #         )
    #         self.control_behavior.arithmetic_conditions.output_signal = result
    #     else:
    #         self.control_behavior.arithmetic_conditions.output_signal = value

    # =========================================================================

    @reissue_warnings
    def set_arithmetic_conditions(
        self,
        first_operand: Union[str, AttrsSignalID, int32, None] = None,
        first_operand_wires: set[Literal["red", "green"]] = {"red", "green"},
        operation: ArithmeticOperation = "*",
        second_operand: Union[str, AttrsSignalID, int32, None] = 0,
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
        # new_control_behavior = {
        #     "arithmetic_conditions": {
        #         "first_signal_networks": {
        #             key: key in first_wires for key in {"red", "green"}
        #         },
        #         "operation": "*" if operation is None else operation,
        #         "second_signal_networks": {
        #             key: key in second_wires for key in {"red", "green"}
        #         },
        #         "output_signal": output_signal,
        #     }
        # }

        # if isinstance(first_operand, int):
        #     new_control_behavior["arithmetic_conditions"][
        #         "first_constant"
        #     ] = first_operand
        # else:
        #     new_control_behavior["arithmetic_conditions"][
        #         "first_signal"
        #     ] = first_operand

        # if isinstance(second_operand, int):
        #     new_control_behavior["arithmetic_conditions"][
        #         "second_constant"
        #     ] = second_operand
        # else:
        #     new_control_behavior["arithmetic_conditions"][
        #         "second_signal"
        #     ] = second_operand

        # # Set
        # self.control_behavior = new_control_behavior
        self.first_operand = first_operand
        self.first_operand_wires = first_operand_wires
        self.operation = operation
        self.second_operand = second_operand
        self.second_operand_wires = second_operand_wires
        self.output_signal = output_signal

    # def remove_arithmetic_conditions(self):
    #     """
    #     Removes the entire ``"arithmetic_conditions"`` key from the control
    #     behavior. This is used to quickly delete the entire condition, and to
    #     tidy up cases where all of the other attributes are set to ``None``, but
    #     the ``"arithmetic_conditions"`` dictionary still exists, taking up space
    #     in the exported string.
    #     """
    #     self.control_behavior.arithmetic_conditions = (
    #         self.Format.ControlBehavior.ArithmeticConditions()
    #     )

    # =========================================================================

    def merge(self, other: "ArithmeticCombinator"):
        super().merge(other)

        self.first_operand = other.first_operand
        self.first_operand_wires = other.first_operand_wires
        self.operation = other.operation
        self.second_operand = other.second_operand
        self.second_operand_wires = other.second_operand_wires
        self.output_signal = other.output_signal

    __hash__ = Entity.__hash__


@attrs.define
class _ExportArithmeticConditions:
    first_signal: Optional[AttrsSignalID] = None
    first_constant: Optional[int32] = None
    second_signal: Optional[AttrsSignalID] = None
    second_constant: Optional[int32] = 0


_export_fields = attrs.fields(_ExportArithmeticConditions)


draftsman_converters.get_version((1, 0)).add_schema(
    {"$id": "factorio:arithmetic_combinator"},
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
        None: fields.first_operand_wires.name,
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
        None: fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
    lambda fields, converter: {
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_constant",
        ): lambda inst: inst.first_operand
        if isinstance(inst.first_operand, int)
        else None,
        (
            "control_behavior",
            "arithmetic_conditions",
            "first_signal",
        ): lambda inst: converter.unstructure(inst.first_operand)
        if not isinstance(inst.first_operand, int)
        else None,
        None: fields.first_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "operation",
        ): fields.operation.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_constant",
        ): lambda inst: inst.second_operand
        if isinstance(inst.second_operand, int)
        else None,
        (
            "control_behavior",
            "arithmetic_conditions",
            "second_signal_signal",
        ): lambda inst: converter.unstructure(inst.second_operand)
        if not isinstance(inst.second_operand, int)
        else None,
        None: fields.second_operand_wires.name,
        (
            "control_behavior",
            "arithmetic_conditions",
            "output_signal",
        ): fields.output_signal.name,
    },
)

# def test(instance: ArithmeticCombinator):
#     res = {
#         "name": instance.name,
#         "position": _unstr_position(instance.global_position)
#     }

draftsman_converters.get_version((2, 0)).add_schema(
    {"$id": "factorio:arithmetic_combinator"},
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
