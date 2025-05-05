# target_priorities.py

from draftsman.signatures import AttrsSimpleCondition, AttrsSignalID, TargetID, int32
from draftsman.validators import instance_of

import attrs
from typing import Literal, Union


@attrs.define(slots=False)
class TargetPrioritiesMixin:
    """
    Enables the entity to prioritize specific targets either statically or
    dynamically via the circuit network.
    """

    priority_list: list[TargetID] = attrs.field(
        factory=list,
        # TODO: converter
        validator=instance_of(list),
    )
    """
    A (static) list of entities to prefer targeting. Overwritten by values given
    by the circuit network if :py:attr:`set_priority_list` is ``True``.
    """

    # @property
    # def priority_list(self) -> Optional[list[TargetID]]:
    #     """
    #     TODO
    #     """
    #     return self._root.priority_list

    # @priority_list.setter
    # def priority_list(self, value: Optional[list[TargetID]]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "priority_list",
    #             value,
    #         )
    #         self._root.priority_list = result
    #     else:
    #         self._root.priority_list = value

    # =========================================================================

    ignore_unprioritized: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to entirely ignore enemies not present in it's 
    :py:attr:`.priority_list`. This value is overridden by the circuit network
    if :py:attr:`.set_ignore_prioritized` is ``True``.
    """

    # @property
    # def ignore_unprioritized(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self._root.ignore_unprioritized

    # @ignore_unprioritized.setter
    # def ignore_unprioritized(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "ignore_unprioritized",
    #             value,
    #         )
    #         self._root.ignore_unprioritized = result
    #     else:
    #         self._root.ignore_unprioritized = value

    # =========================================================================

    set_priority_list: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not priority filters should be set via the circuit network.
    """

    # @property
    # def set_priority_list(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.set_priority_list

    # @set_priority_list.setter
    # def set_priority_list(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "set_priority_list",
    #             value,
    #         )
    #         self.control_behavior.set_priority_list = result
    #     else:
    #         self.control_behavior.set_priority_list = value

    # =========================================================================

    set_ignore_unprioritized: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    If this value is ``True``, the turret will only ignore unprioritized targets
    if the condition :py:attr:`.ignore_unlisted_targets_condition` passes.
    """

    # @property
    # def set_ignore_unlisted_targets(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.set_ignore_unlisted_targets

    # @set_ignore_unlisted_targets.setter
    # def set_ignore_unlisted_targets(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "set_ignore_unlisted_targets",
    #             value,
    #         )
    #         self.control_behavior.set_ignore_unlisted_targets = result
    #     else:
    #         self.control_behavior.set_ignore_unlisted_targets = value

    # =========================================================================

    ignore_unlisted_targets_condition: AttrsSimpleCondition = attrs.field(
        factory=AttrsSimpleCondition,
        converter=AttrsSimpleCondition.converter,
        validator=instance_of(AttrsSimpleCondition),
    )
    """
    The condition to use when determining whether or not to ignore unprioritized
    targets dynamically via the circuit network.
    """

    # =========================================================================

    def set_ignore_unlisted_targets_condition(
        self,
        a: Union[AttrsSignalID, None] = None,
        cmp: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
        b: Union[AttrsSignalID, int32] = 0,
    ):
        """
        Sets the logistic condition of the Entity.

        ``cmp`` can be specified as stored as the single unicode character which
        is used by Factorio, or you can use the Python formatted 2-character
        equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they are converted to and stored as
        the first format.

        :param a: The string name of the first signal.
        :param cmp: The operation to use, as specified above.
        :param b: The string name of the second signal, or some 32-bit constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        self._set_condition("ignore_unlisted_targets_condition", a, cmp, b)

    # def remove_ignore_unlisted_targets_condition(self):
    #     """
    #     Removes the logistic condition of the Entity. Does nothing if the Entity
    #     has no logistic condition to remove.
    #     """
    #     self.control_behavior.ignore_unlisted_targets_condition = None
