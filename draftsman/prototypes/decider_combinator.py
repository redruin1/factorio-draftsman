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
    CircuitNetworkSelection,
    SignalID,
    Comparator,
    int32,
    normalize_comparator,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of, one_of, try_convert

from draftsman.data.entities import decider_combinators

import attrs
import copy
from typing import Literal, Optional


# Matrix of values, where keys are the name of the first_operand and
# the values are sets of signals that cannot be set as output_signal
# TODO: reimplement
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

        first_signal: Optional[SignalID] = attrs.field(
            default=None,
            converter=SignalID.converter,
            validator=instance_of(Optional[SignalID]),
        )
        """
        The left-most signal of the condition.
        """

        first_signal_networks: CircuitNetworkSelection = attrs.field(
            factory=CircuitNetworkSelection,
            converter=CircuitNetworkSelection.converter,
            validator=instance_of(CircuitNetworkSelection),
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

        second_signal: Optional[SignalID] = attrs.field(
            default=None,
            converter=SignalID.converter,
            validator=instance_of(Optional[SignalID]),
        )
        """
        The right-most signal of the condition.
        """

        second_signal_networks: CircuitNetworkSelection = attrs.field(
            factory=CircuitNetworkSelection,
            converter=CircuitNetworkSelection.converter,
            validator=instance_of(CircuitNetworkSelection),
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

    @attrs.define
    class Input(Exportable):
        """
        Purely abstract helper object useful for defining complex decider conditions
        ergonomically.
        """

        signal: SignalID = attrs.field(
            converter=SignalID.converter, validator=instance_of(SignalID)
        )
        """
        TODO
        """
        networks: CircuitNetworkSelection = attrs.field(
            factory=CircuitNetworkSelection,
            converter=CircuitNetworkSelection.converter,
            validator=instance_of(CircuitNetworkSelection),
        )
        """
        TODO
        """

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

        signal: Optional[SignalID] = attrs.field(
            default=None,
            converter=SignalID.converter,
            validator=instance_of(Optional[SignalID]),
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

        networks: CircuitNetworkSelection = attrs.field(
            factory=CircuitNetworkSelection,
            converter=CircuitNetworkSelection.converter,
            validator=instance_of(CircuitNetworkSelection),
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

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return decider_combinators

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    conditions: list[Condition] = attrs.field(
        factory=list,
        validator=instance_of(list[Condition]),
    )
    """
    The list of all circuit conditions that this decider combinator contains.
    Each one is evaluated sequentially (in order) and is conjoined with the 
    previous conditoin either with ``"and"`` or ``"or"``.

    .. NOTE::

        When exporting to Factorio 1.0, only the first condition in this list 
        will end up in the serialized result.
    """

    # =========================================================================

    outputs: list[Output] = attrs.field(
        factory=list,
        validator=instance_of(list[Output]),
    )
    """
    The list of all circuit_outputs that this decider combinator contains.
    Each indivdiual signal or set of signals are combined together on the output
    wire frame.

    .. NOTE::

        When exporting to Factorio 1.0, only the first output in this list will 
        end up in the serialized dictionary.
    """

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
