# infinity_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.error import InvalidFluidError, InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from draftsman.data.entities import infinity_pipes
import draftsman.data.signals as signals

from schema import SchemaError
import six
import warnings


class InfinityPipe(Entity):
    """ """

    def __init__(self, name=infinity_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(InfinityPipe, self).__init__(name, infinity_pipes, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.infinity_settings = kwargs["infinity_settings"]
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def infinity_settings(self):
        # type: () -> dict
        """
        TODO
        """
        return self._infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value):
        # type: (dict) -> None
        if value is None:
            self._infinity_settings = {}
        else:
            try:
                value = signatures.INFINITY_PIPE.validate(value)
                self._infinity_settings = value
            except SchemaError:
                # TODO: more verbose
                raise TypeError("Invalid infinity_settings format")

    # =========================================================================

    @property
    def infinite_fluid_name(self):
        # type: () -> str
        """
        TODO
        """
        return self.infinity_settings.get("name", None)

    @infinite_fluid_name.setter
    def infinite_fluid_name(self, value):
        # type: (str) -> None
        if value is None:
            self.infinity_settings.pop("name", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            if value not in signals.fluid:
                raise InvalidFluidError(value)
            self.infinity_settings["name"] = value
        else:
            raise TypeError("'infinite_fluid_name' must be a str or None")

    # =========================================================================

    @property
    def infinite_fluid_percentage(self):
        # type: () -> int
        """
        TODO
        """
        return self.infinity_settings.get("percentage", None)

    @infinite_fluid_percentage.setter
    def infinite_fluid_percentage(self, value):
        # type: (int) -> None
        if value is None:
            self.infinity_settings.pop("percentage", None)
        elif isinstance(value, (int, float)):
            if value < 0:
                raise ValueError("'percentage' cannot be negative")
            self.infinity_settings["percentage"] = value
        else:
            raise TypeError("'infinite_fluid_percentage' must be a number or None")

    # =========================================================================

    @property
    def infinite_fluid_mode(self):
        # type: () -> str
        """
        TODO
        """
        return self.infinity_settings.get("mode", None)

    @infinite_fluid_mode.setter
    def infinite_fluid_mode(self, value):
        # type: (str) -> None
        if value is None:
            self.infinity_settings.pop("mode", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_modes = {"at-least", "at-most", "exactly", "add", "remove"}
            if value in valid_modes:
                self.infinity_settings["mode"] = value
            else:
                raise InvalidModeError(
                    "'infinite_fluid_mode' ({}) must be one of {}".format(
                        value, valid_modes
                    )
                )
        else:
            raise TypeError("'infinite_fluid_mode' must be a str or None")

    # =========================================================================

    @property
    def infinite_fluid_temperature(self):
        # type: () -> int
        """
        TODO
        """
        return self.infinity_settings.get("temperature", None)

    @infinite_fluid_temperature.setter
    def infinite_fluid_temperature(self, value):
        # type: (int) -> None
        if value is None:
            self.infinity_settings.pop("temperature", None)
        elif isinstance(value, int):
            if not 0 <= value <= 1000:
                warnings.warn(
                    "'infinite_fluid_temperature' ({}) not in range [0, 1000]; "
                    "will be clamped on import".format(value),
                    TemperatureRangeWarning,
                    stacklevel=2,
                )
            self.infinity_settings["temperature"] = value
        else:
            raise TypeError("'temperature' must be an int or None")

    # =========================================================================

    def set_infinite_fluid(
        self, name=None, percentage=0, mode="at-least", temperature=0
    ):
        # type: (str, int, str, int) -> None
        """ """
        try:
            name = signatures.STRING.validate(name)
            percentage = signatures.INTEGER.validate(percentage)
            mode = signatures.STRING.validate(mode)
            temperature = signatures.INTEGER.validate(temperature)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if name not in signals.fluid:
            raise InvalidFluidError(name)
        if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
            raise InvalidModeError(mode)
        # Error if percentage < 0
        if percentage < 0:
            raise ValueError("'percentage' cannot be negative")

        # Warn if temperature is less than 0 or greater than 1000
        if not 0 <= temperature <= 1000:
            warnings.warn(
                "'infinite_fluid_temperature' ({}) not in range [0, 1000]; "
                "will be clamped on import".format(percentage),
                TemperatureRangeWarning,
                stacklevel=2,
            )

        self.infinity_settings["name"] = name
        self.infinity_settings["percentage"] = percentage
        self.infinity_settings["mode"] = mode
        self.infinity_settings["temperature"] = temperature
