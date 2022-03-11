# arithmetic_combinator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import arithmetic_combinators

from typing import Union
import warnings


class ArithmeticCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                           DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = arithmetic_combinators[0], **kwargs):
        # type: (str, **dict) -> None
        super(ArithmeticCombinator, self).__init__(
            name, arithmetic_combinators, **kwargs
        )

        self.dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_arithmetic_conditions(self, a = None, op = "*", b = 0, out = None):
        # type: (Union[str, int], str, Union[str, int], str) -> None
        """
        """
        # TODO: `first_constant`/`second_constant` is incorrect; if there's only
        # one constant it should be just `constant` (because factorio cant make
        # up its damn mind)

        # Check all the parameters before we set anything to preserve original
        a = signatures.SIGNAL_ID_OR_CONSTANT.validate(a)
        op = signatures.OPERATION.validate(op)
        b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
        out = signatures.SIGNAL_ID.validate(out)

        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]
        
        # A
        if a is None: # Default
            arithmetic_conditions.pop("first_signal", None)
            arithmetic_conditions.pop("first_constant", None)
        elif isinstance(a, dict): # Signal Dict
            arithmetic_conditions["first_signal"] = a
            arithmetic_conditions.pop("first_constant", None)
        else: # Constant
            arithmetic_conditions["first_constant"] = a
            arithmetic_conditions.pop("first_signal", None)

        # op
        if op is None:
            arithmetic_conditions.pop("operation", None)
        else:
            arithmetic_conditions["operation"] = op

        # B
        if b is None: # Default
            arithmetic_conditions.pop("second_signal", None)
            arithmetic_conditions.pop("second_constant", None)
        elif isinstance(b, dict): # Signal Dict
            arithmetic_conditions["second_signal"] = b
            arithmetic_conditions.pop("second_constant", None)
        else: # Constant
            arithmetic_conditions["second_constant"] = b
            arithmetic_conditions.pop("second_signal", None)

        # out
        if out is None: # Default
            arithmetic_conditions.pop("output_signal", None)
        else: # Signal Dict
            arithmetic_conditions["output_signal"] = out

    # def set_first_operand(self, operand: Union[str, int]) -> None:
    #     """
    #     """
    #     pass # TODO

    # def set_operation(self, operation: str) -> None:
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

    def remove_arithmetic_conditions(self):
        # type: () -> None
        """
        """
        # TODO: remove
        self.control_behavior.pop("arithmetic_conditions", None)