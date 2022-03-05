# heat_interface.py

from draftsman.prototypes.mixins import Entity
from draftsman.errors import InvalidEntityID, InvalidMode
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import heat_interfaces


class HeatInterface(Entity):
    def __init__(self, name: str = heat_interfaces[0], **kwargs):
        if name not in heat_interfaces:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(HeatInterface, self).__init__(name, **kwargs)

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
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_temperature(self, temperature: int) -> None:
        """
        """
        if temperature is None:
            self.temperature = 0
        else:
            temperature = signatures.INTEGER.validate(temperature)
            assert 0 <= temperature and temperature <= 1000
            self.temperature = temperature

    def set_mode(self, mode: str) -> None:
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
                raise InvalidMode(mode)
            self.mode = mode