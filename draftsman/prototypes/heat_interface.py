# heat_interface.py

from draftsman.prototypes.mixins import Entity
from draftsman.error import InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import heat_interfaces

import warnings


class HeatInterface(Entity):
    def __init__(self, name = heat_interfaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(HeatInterface, self).__init__(name, heat_interfaces, **kwargs)

        self.temperature = 0
        if "temperature" in kwargs:
            self.set_temperature(kwargs["temperature"])
            self.unused_args.pop("temperature")
        self._add_export("temperature", lambda x: x is not None and x != 0)

        self.mode = "at-least"
        if "mode" in kwargs:
            self.set_mode(kwargs["mode"])
            self.unused_args.pop("mode")
        self._add_export("mode", lambda x: x is not None and x != "at-least")

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_temperature(self, temperature):
        # type: (int) -> None
        """
        """
        if temperature is None:
            self.temperature = 0
        else:
            temperature = signatures.INTEGER.validate(temperature)
            assert 0 <= temperature and temperature <= 1000
            self.temperature = temperature

    def set_mode(self, mode):
        # type: (str) -> None
        """
        * "at-least"
        * "at-most"
        * "exactly"
        * "add"
        * "remove"
        """
        if mode is None:
            self.mode = "at-least"
        else:
            if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
                raise InvalidModeError(mode)
            self.mode = mode