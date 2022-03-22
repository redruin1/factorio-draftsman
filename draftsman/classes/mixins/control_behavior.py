# control_behavior.py

from draftsman import signatures

from typing import Union
from schema import SchemaError


class ControlBehaviorMixin(object):
    """
    Enables the entity to specify control behavior.
    TODO: expand
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(ControlBehaviorMixin, self).__init__(
            name, similar_entities, **kwargs
        )

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.control_behavior = kwargs["control_behavior"]
            self.unused_args.pop("control_behavior")
        self._add_export(
            "control_behavior", 
            lambda x: x is not None and len(x) != 0
        )

    # =========================================================================

    @property
    def control_behavior(self):
        # type: () -> dict
        """
        TODO
        """
        return self._control_behavior

    @control_behavior.setter
    def control_behavior(self, value):
        # type: (dict) -> None
        # TODO specific control_behavior signatures depending on the child entity
        if value is None:
            value = {}

        try:
            self._control_behavior = signatures.CONTROL_BEHAVIOR.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid control_behavior format")

    # =========================================================================

    def _set_condition(self, condition_name, a, op, b):
        # type: (str, str, str, Union[str, int]) -> None
        """
        """
        self.control_behavior[condition_name] = {}
        condition = self.control_behavior[condition_name]

        # Check the inputs
        a = signatures.SIGNAL_ID.validate(a)
        op = signatures.COMPARATOR.validate(op)
        b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)

        # A
        if a is None:
            condition.pop("first_signal", None)
        else:
            condition["first_signal"] = a

        # op (should never be None)
        condition["comparator"] = op

        # B (should never be None)
        if isinstance(b, dict):
            condition["second_signal"] = b
            condition.pop("constant", None)
        else: # int
            condition["constant"] = b
            condition.pop("second_signal", None)