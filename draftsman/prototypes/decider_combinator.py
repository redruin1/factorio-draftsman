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
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    int32,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import decider_combinators
from draftsman.signatures import (
    AttrsNetworkSpecification,
    AttrsSignalID,
    Comparator,
    int32,
    normalize_comparator,
)
from draftsman.validators import instance_of, one_of, try_convert

import attrs
import copy
from typing import Literal, Optional


# Matrix of values, where keys are the name of the first_operand and
# the values are sets of signals that cannot be set as output_signal
_signal_blacklist = {
    "signal-everything": {"signal-anything", "signal-each"},
    "signal-anything": {"signal-each"},
    "signal-each": {"signal-everything", "signal-anything"},
}


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

    @attrs.define
    class Condition(Exportable):
        """
        A condition object specifically for DeciderCombinators.
        """

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
        The comparison operation to perform between the two operands.
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
            if isinstance(other, DeciderCombinator.Condition):
                other.compare_type = "or"
                return [copy.copy(self), copy.copy(other)]
            elif isinstance(other, list):
                other[0].compare_type = "or"
                return [copy.copy(self)] + other
            else:
                return NotImplemented

        def __ror__(self, other):
            if isinstance(other, list):
                self.compare_type = "or"
                return other + [copy.copy(self)]
            else:
                return NotImplemented

        def __and__(self, other):
            if isinstance(other, DeciderCombinator.Condition):
                other.compare_type = "and"
                return [copy.copy(self), copy.copy(other)]
            elif isinstance(other, list):
                other[0].compare_type = "and"
                return [copy.copy(self)] + other
            else:
                return NotImplemented

        def __rand__(self, other):
            if isinstance(other, list):
                self.compare_type = "and"
                return other + [copy.copy(self)]
            else:
                return NotImplemented

        @classmethod
        def converter(cls, value):
            if isinstance(value, dict):
                return cls(**value)
            return value

    class Input:  # TODO: does this need to be an attrs class? we probably do want validation at least...
        """
        Purely abstract helper object useful for defining complex decider conditions
        ergonomically.
        """

        def __init__(self, signal, networks: set[str] = {"red", "green"}):
            self.signal = signal
            self.networks = networks

        def _output_condition(self, comparator, other) -> "DeciderCombinator.Condition":
            if isinstance(other, DeciderCombinator.Input):
                return DeciderCombinator.Condition(
                    first_signal=self.signal,
                    first_signal_networks=self.networks,
                    comparator=comparator,
                    second_signal=other.signal,
                    second_signal_networks=other.networks,
                )
            if isinstance(other, (int)):
                return DeciderCombinator.Condition(
                    first_signal=self.signal,
                    first_signal_networks=self.networks,
                    comparator=comparator,
                    constant=other,
                )
            else:
                return NotImplemented

        def __eq__(
            self, other: "DeciderCombinator.Input"
        ) -> "DeciderCombinator.Condition":
            return self._output_condition("=", other)

        def __ne__(self, other) -> "DeciderCombinator.Condition":
            return self._output_condition("!=", other)

        def __gt__(self, other) -> "DeciderCombinator.Condition":
            return self._output_condition(">", other)

        def __lt__(self, other) -> "DeciderCombinator.Condition":
            return self._output_condition("<", other)

        def __ge__(self, other) -> "DeciderCombinator.Condition":
            return self._output_condition(">=", other)

        def __le__(self, other) -> "DeciderCombinator.Condition":
            return self._output_condition("<=", other)

    @attrs.define
    class Output(Exportable):
        """
        An output object specifically for DeciderCombinators.
        """

        signal: Optional[AttrsSignalID] = attrs.field(
            default=None,
            converter=AttrsSignalID.converter,
            validator=instance_of(Optional[AttrsSignalID]),
        )
        """
        The output signal type.
        """

        copy_count_from_input: bool = attrs.field(
            default=True, validator=instance_of(bool)
        )
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

        @classmethod
        def converter(cls, value):
            if isinstance(value, dict):
                return cls(**value)
            return value

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
                res[i] = DeciderCombinator.Condition.converter(elem)
            return res
        return value

    conditions: list[Condition] = attrs.field(
        factory=list,
        converter=_conditions_converter,
        validator=instance_of(list[Condition]),
    )

    # =========================================================================

    def _outputs_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = DeciderCombinator.Output.converter(elem)
            return res
        return value

    outputs: list[Output] = attrs.field(
        factory=list,
        converter=_outputs_converter,
        validator=instance_of(list[Output]),
    )
    """
    TODO
    """

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

    def merge(self, other: "DeciderCombinator"):
        super().merge(other)

        self.conditions = other.conditions
        self.outputs = other.outputs

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    DeciderCombinator.Condition,
    lambda fields: {
        "first_signal": fields.first_signal.name,
        "first_signal_networks": fields.first_signal_networks.name,
        "comparator": fields.comparator.name,
        "constant": fields.constant.name,
        "second_signal": fields.second_signal.name,
        "second_signal_networks": fields.second_signal_networks.name,
        "compare_type": fields.compare_type.name,
    },
)

draftsman_converters.add_hook_fns(
    DeciderCombinator.Output,
    lambda fields: {
        "signal": fields.signal.name,
        "copy_count_from_input": fields.copy_count_from_input.name,
        "networks": fields.networks.name,
        "constant": fields.constant.name,
    },
)

# TODO: write something like this
# draftsman_converters.get_version((1, 0)).add_schema(
#     DeciderCombinator,
#     lambda fields: {
#         # Problem: cannot specify subkeys on the right side
#         # Ideally we would write:
#         ("control_behavior", "decider_conditions", "first_signal"): (fields.conditions.name, 0, "first_signal"),
#         ("control_behavior", "decider_conditions", "comparator"): (fields.conditions.name, 0, "comparator"),
#         ("control_behavior", "decider_conditions", "second_signal"): (fields.conditions.name, 0, "second_signal"),
#         ("control_behavior", "decider_conditions", "output_signal"): (fields.outputs.name, 0, "signal"),
#     }
# )
# Or, we write a pre hook that converts the old format into the new format, but that doesn't work both ways

draftsman_converters.add_hook_fns(
    DeciderCombinator,
    lambda fields: {
        (
            "control_behavior",
            "decider_conditions",
            "conditions",
        ): fields.conditions.name,
        ("control_behavior", "decider_conditions", "outputs"): fields.outputs.name,
    },
)
