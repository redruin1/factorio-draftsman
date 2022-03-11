# infinity_pipe.py

from draftsman.prototypes.mixins import Entity
from draftsman.error import InvalidFluidError, InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import infinity_pipes
import draftsman.data.signals as signals

import warnings


class InfinityPipe(Entity):
    """
    """
    def __init__(self, name = infinity_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(InfinityPipe, self).__init__(name, infinity_pipes, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.set_infinity_settings(kwargs["infinity_settings"])
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_infinity_settings(self, settings):
        # type: (dict) -> None
        """
        """
        if settings is None:
            self.infinity_settings = {}
        else:
            self.infinity_settings = signatures.INFINITY_PIPE.validate(settings)

    def set_infinite_fluid(self, name = None, percentage = 0, mode = "at-least",
                           temperature = 0):
        # type: (str, int, str, int) -> None
        """
        """
        # Check before setting to make sure that we dont partially complete
        name = signatures.STRING.validate(name)
        percentage = signatures.INTEGER.validate(percentage)
        mode = signatures.STRING.validate(mode)
        temperature = signatures.INTEGER.validate(temperature)

        if name not in signals.fluid:
            raise InvalidFluidError(name)
        if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
            raise InvalidModeError(mode)
        # Warn if percentage < 0 or > 100
        # TODO
        # Warn if temperature is less than 0 or greater than 1000
        # TODO 

        self.set_infinite_fluid_name(name)
        self.set_infinite_fluid_percentage(percentage)
        self.set_infinite_fluid_mode(mode)
        self.set_infinite_fluid_temperature(temperature)

    def set_infinite_fluid_name(self, name):
        # type: (str) -> None
        """
        """
        if name is None:
            self.infinity_settings.pop("name", None)
        else:
            name = signatures.STRING.validate(name)
            if name not in signals.fluid:
                raise InvalidFluidError(name)
            self.infinity_settings["name"] = name

    def set_infinite_fluid_percentage(self, percent):
        # type: (int) -> None
        """
        """
        if percent is None:
            self.infinity_settings.pop("percentage", None)
        else:
            percent = signatures.INTEGER.validate(percent)
            self.infinity_settings["percentage"] = percent

    def set_infinite_fluid_mode(self, mode):
        # type: (str) -> None
        """
        """
        if mode is None:
            self.infinity_settings.pop("mode", None)
        else:
            mode = signatures.STRING.validate(mode)
            if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
                raise InvalidModeError(mode)
            self.infinity_settings["mode"] = mode

    def set_infinite_fluid_temperature(self, temperature):
        # type: (int) -> None
        """
        """
        if temperature is None:
            self.infinity_settings.pop("temperature", None)
        else:
            temperature = signatures.INTEGER.validate(temperature)
            self.infinity_settings["temperature"] = temperature