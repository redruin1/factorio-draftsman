# infinity_pipe.py

from draftsman.prototypes.mixins import Entity
from draftsman.errors import InvalidEntityID, InvalidFluidID, InvalidMode
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import infinity_pipes
from draftsman.data.signals import fluid_signals


class InfinityPipe(Entity):
    """
    """
    def __init__(self, name: str = infinity_pipes[0], **kwargs):
        if name not in infinity_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(InfinityPipe, self).__init__(name, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.set_infinity_settings(kwargs["infinity_settings"])
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_infinity_settings(self, settings: dict) -> None:
        """
        """
        if settings is None:
            self.infinity_settings = {}
        else:
            self.infinity_settings = signatures.INFINITY_PIPE.validate(settings)

    def set_infinite_fluid(self, name:str = None, percentage:int = 0, 
                           mode:str = "at-least", temperature:int = 0) -> None:
        """
        """
        # Check before setting to make sure that we dont partially complete
        name = signatures.STRING.validate(name)
        percentage = signatures.INTEGER.validate(percentage)
        mode = signatures.STRING.validate(mode)
        temperature = signatures.INTEGER.validate(temperature)

        if name not in fluid_signals:
            raise InvalidFluidID(name)
        if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
            raise InvalidMode(mode)
        # Warn if percentage < 0 or > 100
        # TODO
        # Warn if temperature is less than 0 or greater than 1000
        # TODO 

        self.set_infinite_fluid_name(name)
        self.set_infinite_fluid_percentage(percentage)
        self.set_infinite_fluid_mode(mode)
        self.set_infinite_fluid_temperature(temperature)

    def set_infinite_fluid_name(self, name: str) -> None:
        """
        """
        if name is None:
            self.infinity_settings.pop("name", None)
        else:
            name = signatures.STRING.validate(name)
            if name not in fluid_signals:
                raise InvalidFluidID(name)
            self.infinity_settings["name"] = name

    def set_infinite_fluid_percentage(self, percent: int):
        """
        """
        if percent is None:
            self.infinity_settings.pop("percentage", None)
        else:
            percent = signatures.INTEGER.validate(percent)
            self.infinity_settings["percentage"] = percent

    def set_infinite_fluid_mode(self, mode: str) -> None:
        """
        """
        if mode is None:
            self.infinity_settings.pop("mode", None)
        else:
            mode = signatures.STRING.validate(mode)
            if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
                raise InvalidMode(mode)
            self.infinity_settings["mode"] = mode

    def set_infinite_fluid_temperature(self, temperature: int) -> None:
        """
        """
        if temperature is None:
            self.infinity_settings.pop("temperature", None)
        else:
            temperature = signatures.INTEGER.validate(temperature)
            self.infinity_settings["temperature"] = temperature