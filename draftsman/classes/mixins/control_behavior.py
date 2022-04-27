# control_behavior.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.error import DataFormatError
from draftsman import signatures

from typing import Union
from schema import SchemaError
import six


class ControlBehaviorMixin(object):
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

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(ControlBehaviorMixin, self).__init__(name, similar_entities, **kwargs)

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.control_behavior = kwargs["control_behavior"]
            self.unused_args.pop("control_behavior")
        self._add_export("control_behavior", lambda x: x is not None and len(x) != 0)

    # =========================================================================

    @property
    def control_behavior(self):
        # type: () -> dict
        """
        The ``control_behavior`` of the Entity.

        :getter: Gets the ``control_behavior``.
        :setter: Sets the ``control_behavior``. Gets set to an empty ``dict`` if
            set to ``None``.
        :type: See :py:data:`draftsman.signatures.CONTROL_BEHAVIOR`

        :exception DataFormatError: If set to anything that does not match the
            ``CONTROL_BEHAVIOR`` signature.
        """
        return self._control_behavior

    @control_behavior.setter
    def control_behavior(self, value):
        # type: (dict) -> None
        # TODO specific control_behavior signatures depending on the child entity
        try:
            self._control_behavior = signatures.CONTROL_BEHAVIOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    def _set_condition(self, condition_name, a, cmp, b):
        # type: (str, str, str, Union[str, int]) -> None
        """
        Single function for setting a condition. Used in `CircuitConditionMixin`
        as well as `LogisticConditionMixin`. Their functionality is identical,
        just with different key names inside `control_behavior`.

        :param condition_name: The string name of the key to set the condition
            under.
        :param a: The string name of the first signal.
        :param cmp: The comparison string.
        :param b: The string name of the second signal, or some integer constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        self.control_behavior[condition_name] = {}
        condition = self.control_behavior[condition_name]

        # Check the inputs
        try:
            a = signatures.SIGNAL_ID_OR_NONE.validate(a)
            cmp = signatures.COMPARATOR.validate(cmp)
            b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        # A
        if a is None:
            condition.pop("first_signal", None)
        else:
            condition["first_signal"] = a

        # op (should never be None)
        condition["comparator"] = cmp

        # B (should never be None)
        if isinstance(b, dict):
            condition["second_signal"] = b
            condition.pop("constant", None)
        else:  # int
            condition["constant"] = b
            condition.pop("second_signal", None)
