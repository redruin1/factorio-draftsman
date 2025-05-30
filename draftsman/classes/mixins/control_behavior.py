# control_behavior.py

from draftsman.classes.exportable import Exportable
from draftsman.signatures import (
    AttrsSimpleCondition,
    AttrsSignalID,
    int32,
)

from typing import Literal, Union


class ControlBehaviorMixin(Exportable):
    """
    Enables the entity to specify control behavior.

    Control behavior is somewhat abstractly defined, but in general it stores
    metadata about how an entity should behave under certain circumstances. It's
    structure is fluid, and contains different valid formats for many different
    Entities. See :py:data:`draftsman.signatures.CONTROL_BEHAVIOR` for a general
    picture of what you might expect inside.

    Because the ``control_behavior`` attribute is used so broadly and in many
    different configurations, individual mixins were designed just to implement
    portions of ``control_behavior``. The following mixins are designed to
    implicitly require this mixin as thier parent:

    * :py:class:`.mixins.circuit_condition.CircuitConditionMixin`
    * :py:class:`.mixins.circuit_read_contents.CircuitReadContentsMixin`
    * :py:class:`.mixins.circuit_read_hand.CircuitReadHandMixin`
    * :py:class:`.mixins.circuit_read_resources.CircuitReadResourceMixin`
    * :py:class:`.mixins.enable_disable.EnableDisableMixin`
    * :py:class:`.mixins.logistic_condition.LogisticConditionMixin`
    * :py:class:`.mixins.mode_of_operation.ModeOfOperationMixin`
    * :py:class:`.mixins.read_rail_signal.ReadRailSignalMixin`
    * :py:class:`.mixins.stack_size.StackSizeMixin`
    """

    def _set_condition(
        self,
        condition_name: str,
        a: Union[AttrsSignalID, None],
        cmp: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="],
        b: Union[AttrsSignalID, int32],
    ):
        """
        Single function for setting a condition. Used in `CircuitConditionMixin`
        as well as `LogisticConditionMixin`. Their functionality is identical,
        just with different key names inside `control_behavior`.

        :param condition_name: The string name of the key to set the condition
            under; either ``circuit_condition`` or ``logistic_condition``.
        :param a: The first signal, it's name, or ``None``.
        :param cmp: The comparator string.
        :param b: The second signal, it's name, or some integer constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        condition = AttrsSimpleCondition(first_signal=a, comparator=cmp)

        # B (should never be None)
        if isinstance(b, int):
            condition.constant = b
        else:
            condition.second_signal = b

        setattr(self, condition_name, condition)

