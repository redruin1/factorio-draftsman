# logistic_condition.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from typing import Union


class LogisticConditionMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to have an logistic enable condition, such as when the
    amount of some item in the logistic network exceeds some constant.
    """

    @property
    def connect_to_logistic_network(self):
        # type: () -> str
        """
        Whether or not this entity should use it's logistic network condition to
        control its operation (if it has one).

        :getter: Gets the value of ``connect_to_logistic_network``, or ``None``
            if not set.
        :setter: Sets the value of ``connect_to_logistic_network``. Removes the
            key if set to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
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

    def set_logistic_condition(self, a=None, cmp="<", b=0):
        # type: (str, str, Union[str, int]) -> None
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
        self._set_condition("logistic_condition", a, cmp, b)

    def remove_logistic_condition(self):
        # type: () -> None
        """
        Removes the logistic condition of the Entity. Does nothing if the Entity
        has no logistic condition to remove.
        """
        self.control_behavior.pop("logistic_condition", None)
