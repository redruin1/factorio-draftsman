# heat_interface.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.error import InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from draftsman.data.entities import heat_interfaces

import warnings


class HeatInterface(Entity):
    """
    An entity that interacts with a heat network.
    """

    def __init__(self, name=heat_interfaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(HeatInterface, self).__init__(name, heat_interfaces, **kwargs)

        self.temperature = 0
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
            self.unused_args.pop("temperature")
        self._add_export("temperature", lambda x: x is not None and x != 0)

        self.mode = "at-least"
        if "mode" in kwargs:
            self.mode = kwargs["mode"]
            self.unused_args.pop("mode")
        self._add_export("mode", lambda x: x is not None and x != "at-least")

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def temperature(self):
        # type: () -> int
        """
        The temperature of the interface in degrees.

        Raises :py:class:`.TemperatureRangeWarning` if set to a value not in the
        range ``[0, 1000]``.

        :getter: Gets the temperature of the interface.
        :setter: Sets the temperature of the interface
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        # type: (int) -> None
        if value is None:
            self._temperature = value
        elif isinstance(value, int):
            if not 0 <= value <= 1000:
                warnings.warn(
                    "'temperature' ({}) not in range [0, 1000]; will be clamped"
                    " on import".format(value),
                    TemperatureRangeWarning,
                    stacklevel=2,
                )
            self._temperature = value
        else:
            raise TypeError("'temperature' must be an int or None")

    # =========================================================================

    @property
    def mode(self):
        # type: () -> str
        """
        Manner in which to interact with the heat network. Can be one of:

        .. code-block:: python

            "at-least"  # At least this hot
            "at-most"   # At most this hot
            "exactly"   # Exactly this temperature
            "add"       # Add this temperature amount each tick
            "remove"    # Remove this temperature amount each tick
            None        # No mode set

        :getter: Gets the mode of the interface.
        :setter: Sets the mode of the interface.
        :type: ``str``

        :exception InvalidModeError: If set to anything other than one of the
            valid strings above or ``None``.
        """
        return self._mode

    @mode.setter
    def mode(self, value):
        # type: (str) -> None
        if value in {"at-least", "at-most", "exactly", "add", "remove", None}:
            self._mode = value
        else:
            raise InvalidModeError(value)
