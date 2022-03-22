# circuit_condition.py

from typing import Union


class CircuitConditionMixin(object): # (ControlBehaviorMixin)
    """
    Allows the Entity to have an circuit enable condition. Used in Pumps, 
    Inserters, Belts, etc.
    """
    def set_enabled_condition(self, a = None, op = "<", b = 0):
        # type: (str, str, Union[str, int]) -> None
        """
        TODO
        """
        self._set_condition("circuit_condition", a, op, b)

    def remove_enabled_condition(self): # TODO: delete
        """
        TODO
        """
        self.control_behavior.pop("circuit_condition", None)