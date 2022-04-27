# enable_disable.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures


class EnableDisableMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to control whether or not it's circuit condition affects
    its operation.
    """

    @property
    def enable_disable(self):
        # type: () -> bool
        """
        Whether or not the machine enables its operation based on the circuit
        condition. Only used on entities that have multiple operation states,
        including (but not limited to) a circuit condition.

        :getter: Gets the value of ``enable_disable``, or ``None`` if not set.
        :setter: Sets the value of ``enable_disable``. Removes the attribute if
            set to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
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
