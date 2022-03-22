# enable_disable.py

from draftsman import signatures


class EnableDisableMixin(object): # (ControlBehaviorMixin)
    """
    Allows the entity to control whether or not it's circuit condition affects
    its operation. Usually used with CircuitConditionMixin.
    """
    @property
    def enable_disable(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("circuit_enable_disable", None)

    @enable_disable.setter
    def enable_disable(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_enable_disable", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_enable_disable"] = value
        else:
            raise TypeError("'enable_disable' must be a bool or None")
        