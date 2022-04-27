# circuit_read_resource.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.constants import MiningDrillReadMode


class CircuitReadResourceMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read the resources underneath it.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_hand.CircuitReadHandMixin`
    """

    @property
    def read_resources(self):
        # type: () -> bool
        """
        Whether or not this Entity is set to read the resources underneath to a
        circuit network.

        :getter: Gets the value of ``read_resources``, or ``None`` if not set.
        :setter: Sets the value of ``read_resources``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.get("circuit_read_resources", None)

    @read_resources.setter
    def read_resources(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_read_resources", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_resources"] = value
        else:
            raise TypeError("'read_resources' must be a bool or None")

    # =========================================================================

    @property
    def read_mode(self):
        # type: () -> MiningDrillReadMode
        """
        The mode in which the resources underneath the Entity should be read.
        Either ``MiningDrillReadMode.UNDER_DRILL`` or
        ``MiningDrillReadMode.TOTAL_PATCH``.

        :getter: Gets the value of ``read_mode``, or ``None`` if not set.
        :setter: Sets the value of ``read_mode``.
        :type: :py:data:`~draftsman.constants.MiningDrillReadMode`

        :exception ValueError: If set to anything other than a
            ``MiningDrillReadMode`` value or their ``int`` equivalent.
        """
        return self.control_behavior.get("circuit_resource_read_mode", None)

    @read_mode.setter
    def read_mode(self, value):
        # type: (MiningDrillReadMode) -> None
        if value is None:
            self.control_behavior.pop("circuit_resource_read_mode", None)
        else:
            value = MiningDrillReadMode(value)
            self.control_behavior["circuit_resource_read_mode"] = value
