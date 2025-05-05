# decider_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.exportable import Exportable
from draftsman.serialization import instance_of
from draftsman.signatures import (
    int32,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.warning import DraftsmanWarning, PureVirtualDisallowedWarning

from draftsman.data.entities import decider_combinators
from draftsman.data import signals
from draftsman.signatures import (
    AttrsNetworkSpecification,
    AttrsSignalID,
    Comparator,
    int32,
    normalize_comparator,
)
from draftsman.utils import reissue_warnings
from draftsman.validators import instance_of, one_of, try_convert

import attrs
from pydantic import ConfigDict, Field, ValidationInfo, model_validator, validate_call
from typing import Any, Literal, Optional, Type, Union


# Matrix of values, where keys are the name of the first_operand and
# the values are sets of signals that cannot be set as output_signal
_signal_blacklist = {
    "signal-everything": {"signal-anything", "signal-each"},
    "signal-anything": {"signal-each"},
    "signal-each": {"signal-everything", "signal-anything"},
}


# Matrix of values, where keys are the name of the first_operand and
# the values are sets of signals that cannot be set as output_signal
_signal_blacklist = {
    "signal-everything": {"signal-anything", "signal-each"},
    "signal-anything": {"signal-each"},
    "signal-each": {"signal-everything", "signal-anything"},
}


@attrs.define
class DeciderCondition(Exportable):
    # class Format(Condition):
    #     compare_type: Optional[Literal["or", "and"]] = Field(
    #         "or",
    #         description="""
    #         Whether or not to boolean OR or AND this condition
    #         with the previous one in the list.
    #         """,
    #     )

    #     model_config = ConfigDict(title="DeciderCondition")

    # def __init__(
    #     self,
    #     first_signal,
    #     first_signal_networks={"red", "green"},
    #     comparator=">",
    #     constant=None,
    #     second_signal=None,
    #     second_signal_networks={"red", "green"},
    #     compare_type="or",
    # ):
    #     # self.first_signal = first_signal
    #     # self.first_signal_networks = first_signal_networks
    #     # self.comparator = comparator
    #     # self.constant = constant
    #     # self.second_signal = second_signal
    #     # self.second_signal_networks = second_signal_networks
    #     # self.compare_type = compare_type

    #     self._root = self.Format.model_validate(
    #         {
    #             "first_signal": first_signal,
    #             "first_signal_networks": first_signal_networks,
    #             "comparator": comparator,
    #             "constant": constant,
    #             "second_signal": second_signal,
    #             "second_signal_networks": second_signal_networks,
    #             "compare_type": compare_type,
    #         },
    #         strict=False,
    #         context={"construction": True, "mode": ValidationMode.NONE},
    #     )

    first_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The left-most signal of the condition.
    """

    first_signal_networks: AttrsNetworkSpecification = attrs.field(
        factory=AttrsNetworkSpecification,
        converter=AttrsNetworkSpecification.converter,
        validator=instance_of(AttrsNetworkSpecification),
    )
    """
    The signal networks (red/green) to sample for the value of the left-most
    signal.
    """

    comparator: Comparator = attrs.field(
        default="<",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    TODO
    """

    constant: Optional[int32] = attrs.field(
        default=None, validator=instance_of(Optional[int32])
    )
    """
    An optional constant value, which always lies on the right side of the 
    condition.
    """

    second_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The right-most signal of the condition.
    """

    second_signal_networks: AttrsNetworkSpecification = attrs.field(
        factory=AttrsNetworkSpecification,
        converter=AttrsNetworkSpecification.converter,
        validator=instance_of(AttrsNetworkSpecification),
    )
    """
    The signal networks (red/green) to sample for the value of the right-most
    signal.
    """

    compare_type: Literal["or", "and"] = attrs.field(
        default="or", validator=one_of("or", "and")
    )

    def __or__(self, other):
        if isinstance(other, DeciderCondition):
            other.compare_type = "or"
            return [self, other]
        elif isinstance(other, list):
            other[0].compare_type = "or"
            return [self] + other
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, DeciderCondition):
            self.compare_type = "or"
            return [other, self]
        elif isinstance(other, list):
            self.compare_type = "or"
            return other + [self]
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, DeciderCondition):
            other.compare_type = "and"
            return [self, other]
        elif isinstance(other, list):
            other[0].compare_type = "and"
            return [self] + other
        else:
            return NotImplemented

    def __rand__(self, other):
        if isinstance(other, DeciderCondition):
            self.compare_type = "and"
            return [other, self]
        elif isinstance(other, list):
            self.compare_type = "and"
            return other + [self]
        else:
            return NotImplemented

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


class DeciderInput:  # TODO: does this need to be an attrs class? we probably do want validation at least...
    """
    Purely abstract helper object useful for defining complex decider conditions
    ergonomically.
    """

    def __init__(self, signal, networks: set[str] = {"red", "green"}):
        self.signal = signal
        self.networks = networks

    def _output_condition(self, comparator, other) -> DeciderCondition:
        if isinstance(other, DeciderInput):
            return DeciderCondition(
                first_signal=self.signal,
                first_signal_networks=self.networks,
                comparator=comparator,
                second_signal=other.signal,
                second_signal_networks=other.networks,
            )
        if isinstance(other, (int)):
            return DeciderCondition(
                first_signal=self.signal,
                first_signal_networks=self.networks,
                comparator=comparator,
                constant=other,
            )
        else:
            return NotImplemented

    def __eq__(self, other: "DeciderInput") -> DeciderCondition:
        return self._output_condition("=", other)

    def __ne__(self, other) -> DeciderCondition:
        return self._output_condition("!=", other)

    def __gt__(self, other) -> DeciderCondition:
        return self._output_condition(">", other)

    def __lt__(self, other) -> DeciderCondition:
        return self._output_condition("<", other)

    def __ge__(self, other) -> DeciderCondition:
        return self._output_condition("<=", other)

    def __le__(self, other) -> DeciderCondition:
        return self._output_condition(">=", other)


@attrs.define
class DeciderOutput(Exportable):  # TODO: Exportable
    # class Format(DraftsmanBaseModel):
    #     signal: AttrsSignalID = Field(..., description="""The signal type to output.""")
    #     copy_count_from_input: Optional[bool] = Field(
    #         True,
    #         description="""
    #         Broadcasts the given input value to the output if true, or a unit
    #         value if false.
    #         """,
    #     )
    #     networks: Optional[NetworkSpecification] = Field(
    #         NetworkSpecification(red=True, green=True),
    #         description="""What wires this output should be broadcast to.""",
    #     )
    #     constant: Optional[int32] = Field(
    #         1,
    #         description="""
    #         What value the constant output should be if "copy_count_from_input"
    #         is false. Always specified as 1 in game, but can be overwritten
    #         externally and will be respected.
    #         """,
    #     )

    #     model_config = ConfigDict(title="DeciderOutput")

    signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The output signal type.
    """

    copy_count_from_input: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to source the output signal(s) value from the input wires, or
    to output them with constant values as specified by :py:attr:`.constant`.
    """

    networks: AttrsNetworkSpecification = attrs.field(
        factory=AttrsNetworkSpecification,
        converter=AttrsNetworkSpecification.converter,
        validator=instance_of(AttrsNetworkSpecification),
    )
    """
    Which wire networks to sample values from (red/green).
    """

    constant: int32 = attrs.field(default=1, validator=instance_of(int32))
    """
    The constant value to output to the network, if 
    :py:attr:`.copy_count_from_input` is ``False``. Can be any signed 32-bit 
    number.
    """

    # def __init__(
    #     self, signal, copy_count_from_input=True, constant=1, networks={"red", "green"}
    # ):
    #     self._root: DeciderOutput.Format
    #     self._root = self.__class__.Format.model_validate(
    #         {
    #             "signal": signal,
    #             "copy_count_from_input": copy_count_from_input,
    #             "constant": constant,
    #             "networks": networks,
    #         },
    #         strict=False,
    #         context={"construction": True, "mode": ValidationMode.NONE},
    #     )

    # @property
    # def signal(self):
    #     return self._root.signal

    # @property
    # def copy_count_from_input(self):
    #     return self._root.copy_count_from_input

    # @property
    # def constant(self):
    #     return self._root.constant

    # @property
    # def networks(self):
    #     return self._root.networks

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


@fix_incorrect_pre_init
@attrs.define
class DeciderCombinator(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    A decider combinator. Makes comparisons based on circuit network inputs.
    """

    # Alias the external objects so we can access them easily without importing
    Input = DeciderInput
    Condition = DeciderCondition
    Output = DeciderOutput

    # @attrs.define
    # class Input:
    #     pass

    # @attrs.define
    # class Condition:
    #     pass

    # 1.0 format
    # class Format(
    #     PlayerDescriptionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         class DeciderConditions(Condition):
    #             output_signal: Optional[SignalID] = Field(
    #                 None,
    #                 description="""
    #                 The output signal to output if the condition is met. The
    #                 value of the output signal is determined by the
    #                 'copy_count_from_input' key.
    #                 """,
    #             )
    #             copy_count_from_input: Optional[bool] = Field(
    #                 True,
    #                 description="""
    #                 Whether or not to copy the value of the selected output
    #                 signal from the input circuit network, or to output the
    #                 selected 'output_signal' with a value of 1.
    #                 """,
    #             )

    #             @model_validator(mode="after")
    #             def ensure_proper_signal_configuration(self, info: ValidationInfo):
    #                 """
    #                 The first signal and output signals can be pure virtual
    #                 signals, but only in a certain configuration as determined
    #                 by `_signal_blacklist`. If the input signal is not a pure
    #                 virtual signal, then the output signal cannot be
    #                 `"signal-anything"` or `"signal-each"`.
    #                 """
    #                 if not info.context or self.output_signal is None:
    #                     return self
    #                 if info.context["mode"] <= ValidationMode.MINIMUM:
    #                     return self

    #                 warning_list: list = info.context["warning_list"]

    #                 if self.first_signal is None:
    #                     first_signal_name = None
    #                 else:
    #                     first_signal_name = self.first_signal.name

    #                 current_blacklist = _signal_blacklist.get(
    #                     first_signal_name, {"signal-anything", "signal-each"}
    #                 )
    #                 if self.output_signal.name in current_blacklist:
    #                     warning_list.append(
    #                         PureVirtualDisallowedWarning(
    #                             "'{}' cannot be an output_signal when '{}' is the first operand; 'output_signal' will be removed when imported".format(
    #                                 self.output_signal.name, first_signal_name
    #                             ),
    #                         )
    #                     )

    #                 return self

    #             @model_validator(mode="after")
    #             def ensure_second_signal_is_not_pure_virtual(
    #                 self, info: ValidationInfo
    #             ):
    #                 if not info.context or self.second_signal is None:
    #                     return self
    #                 if info.context["mode"] <= ValidationMode.MINIMUM:
    #                     return self

    #                 warning_list: list = info.context["warning_list"]

    #                 if self.second_signal.name in signals.pure_virtual:
    #                     warning_list.append(
    #                         PureVirtualDisallowedWarning(
    #                             "'second_signal' cannot be set to pure virtual signal '{}'; will be removed when imported".format(
    #                                 self.second_signal.name
    #                             )
    #                         )
    #                     )

    #                 return self

    #         decider_conditions: Optional[DeciderConditions] = DeciderConditions()

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="DeciderCombinator")

    # class Format(
    #     PlayerDescriptionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         class DeciderConditions(DraftsmanBaseModel):
    #             # class Output(DraftsmanBaseModel):
    #             #     signal: SignalID
    #             #     copy_count_from_input: bool = Field(
    #             #         True,
    #             #         description="""
    #             #         Whether or not to copy the value of the selected output
    #             #         signal from the input circuit network, or to output the
    #             #         selected 'output_signal' with a value of 1.
    #             #         """,
    #             #     )
    #             #     networks: Optional[NetworkSpecification] = Field(
    #             #         NetworkSpecification(red=True, green=True),
    #             #         description="""
    #             #         What wires to pull values from if 'copy_count_from_input'
    #             #         is true.""",
    #             #     )

    #             conditions: list = Field(
    #                 [],
    #                 description="""
    #                 A list of Condition objects specifying when (and what) this
    #                 decider combinator should output.""",
    #             )
    #             outputs: list = Field(
    #                 [],
    #                 description="""
    #                 A list of Output objects specifying what signals should be
    #                 passed to the output wire when the conditions evaluate to
    #                 true.
    #                 """,
    #             )

    #             # @model_validator(mode="after")
    #             # def ensure_proper_signal_configuration(self, info: ValidationInfo):
    #             #     """
    #             #     The first signal and output signals can be pure virtual
    #             #     signals, but only in a certain configuration as determined
    #             #     by `_signal_blacklist`. If the input signal is not a pure
    #             #     virtual signal, then the output signal cannot be
    #             #     `"signal-anything"` or `"signal-each"`.
    #             #     """
    #             #     if not info.context or self.output_signal is None:
    #             #         return self
    #             #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #             #         return self

    #             #     warning_list: list = info.context["warning_list"]

    #             #     if self.first_signal is None:
    #             #         first_signal_name = None
    #             #     else:
    #             #         first_signal_name = self.first_signal.name

    #             #     current_blacklist = _signal_blacklist.get(
    #             #         first_signal_name, {"signal-anything", "signal-each"}
    #             #     )
    #             #     if self.output_signal.name in current_blacklist:
    #             #         warning_list.append(
    #             #             PureVirtualDisallowedWarning(
    #             #                 "'{}' cannot be an output_signal when '{}' is the first operand; 'output_signal' will be removed when imported".format(
    #             #                     self.output_signal.name, first_signal_name
    #             #                 ),
    #             #             )
    #             #         )

    #             #     return self

    #         decider_conditions: Optional[DeciderConditions] = DeciderConditions()

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="DeciderCombinator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(decider_combinators),
    #     position: Union[Vector, PrimitiveVector, None] = None,
    #     tile_position: Union[Vector, PrimitiveVector, None] = (0, 0),
    #     direction: Optional[Direction] = Direction.NORTH,
    #     player_description: Optional[str] = None,
    #     control_behavior: Optional[Format.ControlBehavior] = None,
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
    #         decider_combinators,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         player_description=player_description,
    #         control_behavior={} if control_behavior is None else control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return decider_combinators

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    def _conditions_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = DeciderCondition.converter(elem)
            return res
        return value

    conditions: list[Condition] = attrs.field(
        factory=list,
        converter=_conditions_converter,
        validator=instance_of(list),  # TODO: validators
    )

    # @property
    # def conditions(self) -> list[Condition]:
    #     return self.control_behavior.decider_conditions.conditions

    # @conditions.setter
    # def conditions(self, value: list[Condition]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "conditions",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.conditions = result
    #     else:
    #         self.control_behavior.decider_conditions.conditions = value

    # =========================================================================

    def _outputs_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = DeciderOutput.converter(elem)
            return res
        return value

    outputs: list[Output] = attrs.field(
        factory=list,
        converter=_outputs_converter,
        validator=instance_of(list),  # TODO: validators
    )

    # @property
    # def outputs(self) -> list[DeciderOutput]:
    #     return self.control_behavior.decider_conditions.outputs

    # @outputs.setter
    # def outputs(self, value: Optional[list[DeciderOutput]]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "outputs",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.outputs = result
    #     else:
    #         self.control_behavior.decider_conditions.outputs = value

    # @property
    # def first_operand(self) -> Union[SignalID, None]:
    #     """
    #     The first operand of the ``DeciderCombinator``. Must be a signal or ``None``;
    #     cannot be a constant. Has a number of restrictions on which of the
    #     "special" signals can be in this position in relation to
    #     :py:attr:`.output_signal`:

    #     .. list-table::
    #         :header-rows: 1

    #         * - ``first_operand`` value
    #           - Valid ``output_signal`` value(s)
    #         * - All Normal Signals
    #           - | All Normal Signals,
    #             | ``"signal-everything"``
    #         * - ``"signal-everything"``
    #           - | All Normal Signals,
    #             | ``"signal-everything"``
    #         * - ``"signal-anything"``
    #           - | All Normal Signals,
    #             | ``"signal-everything"``,
    #             | ``"signal-anything"``
    #         * - ``"signal-each"``
    #           - | All Normal Signals,
    #             | ``"signal-each"``

    #     If ``first_operand`` is set to something that makes ``output_signal``
    #     fall outside of these accepted values, then ``output_signal`` is reset
    #     to ``None``.

    #     :getter: Gets the first operand of the operation, or ``None`` if not set.
    #     :setter: Sets the first operand of the operation. Removes the key if set
    #         to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.decider_conditions.first_signal

    # @first_operand.setter
    # def first_operand(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "first_signal",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.first_signal = result
    #     else:
    #         self.control_behavior.decider_conditions.first_signal = value

    # =========================================================================

    # @property
    # def operation(self) -> Literal[">", "<", "=", "≥", "≤", "≠", None]:
    #     """
    #     The operation of the ``DeciderCombinator`` Can be specified as the
    #     single unicode character which is used by Factorio, or you can use the
    #     Python formatted 2-character equivalents::

    #         # One of:
    #         [">", "<", "=",  "≥",  "≤",  "≠"]
    #         # Or, alternatively:
    #         [">", "<", "==", ">=", "<=", "!="]

    #     or ``None``. If specified in the second format, they are converted to
    #     and stored as the first format.

    #     :getter: Gets the current operation, or ``None`` if not set.
    #     :setter: Sets the current operation. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than one of the values
    #         specified above.
    #     """
    #     return self.control_behavior.decider_conditions.comparator

    # @operation.setter
    # def operation(
    #     self, value: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!=", None]
    # ):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "comparator",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.comparator = result
    #     else:
    #         self.control_behavior.decider_conditions.comparator = value

    # =========================================================================

    # @property
    # def second_operand(self) -> Union[SignalID, int32, None]:
    #     """
    #     The second operand of the ``DeciderCombinator``. Cannot be one of the
    #     :py:data:`.pure_virtual` signals, which is forbidden for this operand in
    #     combinators of this type.

    #     :getter: Gets the second operand of the operation, or ``None`` if not
    #         set.
    #     :setter: Sets the second operand of the operation. Removes the key if
    #         set to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID``, an
    #         ``int``, or ``None``.
    #     :exception DraftsmanError: If set to a pure virtual signal, which is
    #         forbidden.
    #     """
    #     decider_conditions = self.control_behavior.decider_conditions
    #     if not decider_conditions:
    #         return None

    #     if decider_conditions.second_signal is not None:
    #         return decider_conditions.second_signal
    #     elif decider_conditions.constant is not None:
    #         return decider_conditions.constant
    #     else:
    #         return None

    # @second_operand.setter
    # def second_operand(
    #     self, value: Union[str, SignalID, int32, None]
    # ):  # TODO: SignalName(?)
    #     # if self.validate_assignment:
    #     #     value = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format.ControlBehavior.DeciderConditions,
    #     #         self.control_behavior.decider_conditions,
    #     #         "second_operand",
    #     #         value
    #     #     )
    #     #     self.control_behavior.decider_conditions.second_operand = result
    #     # else:
    #     #     self.control_behavior.decider_conditions.second_operand = value

    #     if value is None:  # Default
    #         self.control_behavior.decider_conditions.second_signal = None
    #         self.control_behavior.decider_conditions.constant = None
    #     elif isinstance(value, (int, float)):  # Constant
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.DeciderConditions,
    #                 self.control_behavior.decider_conditions,
    #                 "constant",
    #                 value,
    #             )
    #         self.control_behavior.decider_conditions.constant = value
    #         self.control_behavior.decider_conditions.second_signal = None
    #     else:  # Signal or other
    #         if self.validate_assignment:
    #             value = attempt_and_reissue(
    #                 self,
    #                 type(self).Format.ControlBehavior.DeciderConditions,
    #                 self.control_behavior.decider_conditions,
    #                 "second_signal",
    #                 value,
    #             )
    #         self.control_behavior.decider_conditions.second_signal = value
    #         self.control_behavior.decider_conditions.constant = None

    # =========================================================================

    # @property
    # def output_signal(self) -> Optional[SignalID]:
    #     """
    #     The output signal of the ``ArithmeticCombinator``.

    #     :getter: Gets the output signal, or ``None`` if not set.
    #     :setter: Sets the output signal. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``SIGNAL_ID`` or
    #         ``None``.
    #     :exception DraftsmanError: If set to a value which conflicts with
    #         :py:attr:`.first_operand`; see that attribute for more information.
    #     """
    #     return self.control_behavior.decider_conditions.output_signal

    # @output_signal.setter
    # def output_signal(self, value: Union[str, SignalID]):  # TODO: SignalName?
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "output_signal",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.output_signal = result
    #     else:
    #         self.control_behavior.decider_conditions.output_signal = value

    # =========================================================================

    # @property
    # def copy_count_from_input(self) -> Optional[bool]:
    #     """
    #     Whether or not the input value of a signal is transposed to the output
    #     signal. If this is false, the output signal is output with a value of 1
    #     if the condition is met. A default of ``None`` means ``True``.

    #     :getter: Gets whether or not to copy the value, or ``None`` is not set.
    #     :setter: Sets whether or not to copy the value. Removes the key if set
    #         to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.decider_conditions.copy_count_from_input

    # @copy_count_from_input.setter
    # def copy_count_from_input(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.DeciderConditions,
    #             self.control_behavior.decider_conditions,
    #             "copy_count_from_input",
    #             value,
    #         )
    #         self.control_behavior.decider_conditions.copy_count_from_input = result
    #     else:
    #         self.control_behavior.decider_conditions.copy_count_from_input = value

    # =========================================================================

    # @reissue_warnings
    # def set_decider_conditions(
    #     self,
    #     first_operand: Union[str, SignalID, None] = None,
    #     operation: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
    #     second_operand: Union[str, SignalID, int32, None] = 0,
    #     output_signal: Union[str, SignalID, None] = None,
    #     copy_count_from_input: bool = True,
    # ):
    #     """
    #     Set the operation for the ``DeciderCombinator`` all at once. All of the
    #     restrictions to the individual attributes still apply.

    #     :param first_operand: The name of the first signal to set, or ``None``.
    #     :param operation: The comparison operator to use. See :py:data:`.COMPARATOR`
    #         for more information on valid values.
    #     :param second_operand: The name of the second signal, some constant, or
    #         ``None``.
    #     :param output_signal: The name of the output signal to set, or ``None``.
    #     :param copy_count_from_input: Whether or not to copy input signal values
    #         to output signal values. Defaults to ``None``, which also means ``True``.

    #     :exception DataFormatError: If the any of the arguments fail to match
    #         their correct formats.
    #     """
    #     new_control_behavior = {
    #         "decider_conditions": {
    #             "first_signal": first_operand,
    #             "comparator": operation,
    #             "output_signal": output_signal,
    #             "copy_count_from_input": copy_count_from_input,
    #         }
    #     }

    #     if isinstance(second_operand, (int, float)):
    #         new_control_behavior["decider_conditions"]["constant"] = second_operand
    #     else:
    #         new_control_behavior["decider_conditions"]["second_signal"] = second_operand

    #     # Set
    #     self.control_behavior = new_control_behavior

    # def remove_decider_conditions(self):
    #     """
    #     Wipes all the values from the ``"decider_conditions"`` key in this
    #     entity's control behavior. Allows you to quickly clear all values
    #     associated with this entity without having to manually reset each
    #     attribute.
    #     """
    #     self.control_behavior.decider_conditions = (
    #         __class__.Format.ControlBehavior.DeciderConditions()
    #     )

    # =========================================================================

    __hash__ = Entity.__hash__
