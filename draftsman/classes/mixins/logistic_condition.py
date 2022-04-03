# logistic_condition.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from typing import Union


class LogisticConditionMixin(object):  # (ControlBehaviorMixin)
    """
    Gives the Entity the capablility to be logistic network controlled.
    """

    @property
    def connect_to_logistic_network(self):
        # type: () -> str
        """
        TODO
        """
        return self.control_behavior.get("connect_to_logistic_network", None)

    @connect_to_logistic_network.setter
    def connect_to_logistic_network(self, value):
        if value is None:
            self.control_behavior.pop("connect_to_logistic_network", None)
        elif isinstance(value, bool):
            self.control_behavior["connect_to_logistic_network"] = value
        else:
            raise TypeError("'connect_to_logistic_network' must be a bool or None")

    # =========================================================================

    def set_logistic_condition(self, a=None, op="<", b=0):
        # type: (str, str, Union[str, int]) -> None
        """ """
        self._set_condition("logistic_condition", a, op, b)

    def remove_logistic_condition(self):  # TODO: delete
        """ """
        self.control_behavior.pop("logistic_condition", None)
