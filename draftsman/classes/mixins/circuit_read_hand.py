# circuit_read_hand.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import ReadMode


class CircuitReadHandMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read it's hand's contents.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_resource.CircuitReadResourceMixin`
    """

    @property
    def read_hand_contents(self):
        # type: () -> bool
        """
        Whether or not this Entity is set to read the contents of it's hand to a
        circuit network.

        :getter: Gets the value of ``read_hand_contents``, or ``None`` if not
            set.
        :setter: Sets the value of ``read_hand_contents``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.get("circuit_read_hand_contents", None)

    @read_hand_contents.setter
    def read_hand_contents(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_read_hand_contents", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_hand_contents"] = value
        else:
            raise TypeError("'read_hand_contents' must be a bool or None")

    # =========================================================================

    @property
    def read_mode(self):
        # type: () -> ReadMode
        """
        The mode in which the contents of the Entity should be read. Either
        ``ReadMode.PULSE`` or ``ReadMode.HOLD``.

        :getter: Gets the value of ``read_mode``, or ``None`` if not set.
        :setter: Sets the value of ``read_mode``.
        :type: :py:data:`~draftsman.constants.ReadMode`

        :exception ValueError: If set to anything other than a ``ReadMode``
            value or their ``int`` equivalent.
        """
        return self.control_behavior.get("circuit_hand_read_mode", None)

    @read_mode.setter
    def read_mode(self, value):
        # type: (ReadMode) -> None
        if value is None:
            self.control_behavior.pop("circuit_hand_read_mode", None)
        else:
            self.control_behavior["circuit_hand_read_mode"] = ReadMode(value)
