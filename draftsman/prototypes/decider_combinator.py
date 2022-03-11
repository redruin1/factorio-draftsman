# decider_combinator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import decider_combinators

from typing import Union
import warnings


class DeciderCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                        DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = decider_combinators[0], **kwargs):
        # type: (str, **dict) -> None
        super(DeciderCombinator, self).__init__(
            name, decider_combinators, **kwargs
        )

        self.dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )
    
    def set_decider_conditions(self, a = None, op = "<", b = 0, out = None):
        # type: (Union[str, int], str, Union[str, int], str) -> None
        """
        """
        # TODO: `first_constant`/`second_constant` is incorrect; if there's only
        # one constant it should be just `constant` (because factorio cant make
        # up its damn mind)

        # Check all the parameters before we set anything to preserve original
        a = signatures.SIGNAL_ID_OR_CONSTANT.validate(a)
        op = signatures.COMPARATOR.validate(op)
        b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
        out = signatures.SIGNAL_ID.validate(out)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]

        # A
        if a is None: # Default
            decider_conditions.pop("first_signal", None)
            decider_conditions.pop("first_constant", None)
        elif isinstance(a, dict): # Signal Dict
            decider_conditions["first_signal"] = a
            decider_conditions.pop("first_constant", None)
        else: # Constant
            decider_conditions["first_constant"] = a
            decider_conditions.pop("first_signal", None)

        # op
        if op is None:
            decider_conditions.pop("comparator", None)
        else:
            decider_conditions["comparator"] = op

        # B
        if b is None: # Default
            decider_conditions.pop("second_signal", None)
            decider_conditions.pop("second_constant", None)
        elif isinstance(b, dict): # Signal Dict
            decider_conditions["second_signal"] = b
            decider_conditions.pop("second_constant", None)
        else: # Constant
            decider_conditions["second_constant"] = b
            decider_conditions.pop("second_signal", None)

        # out
        if out is None: # Default
            decider_conditions.pop("output_signal", None)
        else: # Signal Dict
            decider_conditions["output_signal"] = out

    # def set_first_operand(self, operand: Union[str, int]) -> None:
    #     """
    #     """
    #     pass # TODO

    # def set_comparator(self, comparator: str) -> None:
    #     """
    #     """
    #     pass # TODO

    # def set_second_operand(self, operand: Union[str, int]) -> None:
    #     """
    #     """
    #     pass # TODO

    # def set_output_signal(self, out:str) -> None:
    #     """
    #     """
    #     pass # TODO

    def set_copy_count_from_input(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior["decider_conditions"].pop(
                "copy_count_from_input", None
            )
        else:
            if "decider_conditions" not in self.control_behavior:
                self.control_behavior["decider_conditions"] = {}
            decider_conditions = self.control_behavior["decider_conditions"]
            value = signatures.BOOLEAN.validate(value)
            decider_conditions["copy_count_from_input"] = value

    def remove_decider_conditions(self):
        # type: () -> None
        """
        """
        # TODO: delete this function
        self.control_behavior.pop("decider_conditions", None)