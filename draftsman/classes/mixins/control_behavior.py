# control_behavior.py

from draftsman.classes.exportable import Exportable
from draftsman.signatures import (
    Comparator,
    Condition,
    SignalID,
    int32,
)

from typing import Union


class ControlBehaviorMixin(Exportable):
    """
    Enables the entity to specify control behavior.
    """

    def _set_condition(
        self,
        condition_name: str,
        first_operand: Union[SignalID, None],
        comparator: Comparator,
        second_operand: Union[SignalID, int32],
    ):
        """
        Single function for setting a condition. Used in `CircuitConditionMixin`
        as well as `LogisticConditionMixin`. Their functionality is identical,
        just with different key names inside `control_behavior`.

        :param condition_name: The string name of the key to set the condition
            under.
        :param first_operand: The first signal, it's name, or ``None``.
        :param comparator: The comparator string.
        :param second_operand: The second signal, it's name, or some integer constant.

        :exception DataFormatError: If ``first_operand`` is not a valid signal
            name, if ``comparator`` is not a valid operation, or if
            ``second_operand`` is neither a valid signal name nor a constant.
        """
        condition = Condition(first_signal=first_operand, comparator=comparator)

        # B (should never be None)
        if isinstance(second_operand, int):
            condition.constant = second_operand
        else:
            condition.second_signal = second_operand

        setattr(self, condition_name, condition)
