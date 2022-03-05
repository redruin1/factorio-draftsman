# decider_combinator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
from typing import Union
import draftsman.signatures as signatures

from draftsman.data.entities import decider_combinators


class DeciderCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                        DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = decider_combinators[0], **kwargs):
        if name not in decider_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(DeciderCombinator, self).__init__(name, **kwargs)

        self.dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_decider_conditions(self, a:Union[str,int] = None, op:str = "<", 
                               b:Union[str,int] = 0, out:str = None) -> None:
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

    def set_copy_count_from_input(self, value: bool) -> None:
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
        """
        """
        # TODO: delete this function
        self.control_behavior.pop("decider_conditions", None)