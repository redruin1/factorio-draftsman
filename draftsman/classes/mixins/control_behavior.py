# control_behavior.py

from draftsman.error import DataFormatError
from draftsman.signatures import (
    AttrsSimpleCondition,
    AttrsSignalID,
    int32,
)

from typing import Literal, Union


class ControlBehaviorMixin:
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

    # class Format(DraftsmanBaseModel):
    #     # TODO: It would be nice if we could specify "control_behavior" as an
    #     # abstract field, so that any sub-Format that inherits ControlBehavior
    #     # must implement it
    #     # `control_behavior: AbstractField` or something
    #     pass

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    # Have to do a bit of forward-lookahead to grab the correct control_behavior
    # self.control_behavior = kwargs.get(
    #     "control_behavior", type(self).Format.ControlBehavior()
    # )

    # =========================================================================

    # @property
    # def control_behavior(self):
    #     """
    #     The ``control_behavior`` of the Entity.

    #     :getter: Gets the ``control_behavior``.
    #     :setter: Sets the ``control_behavior``. Gets set to an empty ``dict`` if
    #         set to ``None``.

    #     :exception DataFormatError: If set to anything that does not match the
    #         ``CONTROL_BEHAVIOR`` signature.
    #     """
    #     return self._root.control_behavior

    # @control_behavior.setter
    # def control_behavior(self, value):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "control_behavior", value
    #         )
    #         self._root.control_behavior = result
    #     else:
    #         self._root.control_behavior = value

    # =========================================================================

    # def merge(self, other):
    #     super().merge(other)

    #     self.control_behavior = other.control_behavior

    # =========================================================================

    # def to_dict(
    #     self, exclude_none: bool = True, exclude_defaults: bool = True
    # ) -> dict:  # TODO: FIXME
    #     result = super().to_dict(
    #         exclude_none=exclude_none, exclude_defaults=exclude_defaults
    #     )
    #     if "control_behavior" in result and result["control_behavior"] == {}:
    #         del result["control_behavior"]
    #     return result

    # =========================================================================

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
