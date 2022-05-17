# infinity_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.error import InvalidFluidError, InvalidModeError, DataFormatError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from draftsman.data.entities import infinity_pipes
import draftsman.data.signals as signals

from schema import SchemaError
import six
import warnings


class InfinityPipe(Entity):
    """
    An entity used to create an infinite amount of any fluid at any temperature.
    """

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
        The settings that control the manner in which what fluid is spawned or
        removed.

        :getter: Gets the ``infinity_settings`` of the ``InfinityPipe``.
        :setter: Sets the ``infinity_settings`` of the ``InfinityPipe``.
            Defaults to an empty ``dict`` if set to ``None``.
        :type: :py:data:`.INFINITY_PIPE`

        :exception DataFormatError: If set to anything that does not match the
            :py:data:`.INFINITY_PIPE` format.
        """
        return self._infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value):
        # type: (dict) -> None
        try:
            value = signatures.INFINITY_PIPE.validate(value)
            self._infinity_settings = value
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def infinite_fluid_name(self):
        # type: () -> str
        """
        Sets the name of the infinite fluid.

        :getter: Gets the infinite fluid name, or ``None`` if not set.
        :setter: Sets the infinite fluid name. Removes the key if set to ``None``.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidFluidError: If set to an invalid fluid name.
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
        The percentage of the infinite fluid in the pipe, where ``1.0`` is 100%.

        :getter: Gets the percentage full, or ``None`` if not set.
        :setter: Sets the percentage full. Removes the key if set to ``None``.
        :type: float

        :exception TypeError: If set to anything other than an number or ``None``.
        :exception ValueError: If set to a negative percentage, which is forbidden.
        """
        return self.infinity_settings.get("percentage", None)

    @infinite_fluid_percentage.setter
    def infinite_fluid_percentage(self, value):
        # type: (int) -> None
        if value is None:
            self.infinity_settings.pop("percentage", None)
        elif isinstance(value, (float, int)):
            if value < 0:
                raise ValueError("'percentage' cannot be negative")
            self.infinity_settings["percentage"] = float(value)
        else:
            raise TypeError("'infinite_fluid_percentage' must be a number or None")

    # =========================================================================

    @property
    def infinite_fluid_mode(self):
        # type: () -> str
        """
        The mode in which to manage the infinite fluid. Can be one of:

        .. code-block:: python

            "at-least"  # At least this much fluid
            "at-most"   # At most this much fluid
            "exactly"   # Exactly this much fluid
            "add"       # Add this much fluid each tick
            "remove"    # Remove this much fluid each tick

        :getter: Gets the fluid mode, or ``None`` if not set.
        :setter: Sets the fluid mode. Removes the key if set to ``None``.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidModeError: If set to anything other than one of the
            values described above.
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
        # type: () -> float
        """
        The temperature of the infinite fluid, in degrees.

        Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
        anything not in the range ``[0, 1000]``.

        :getter: Gets the fluid temperature, or ``None`` if not set.
        :setter: Sets the fluid temperature. Removes the key if set to ``None``.
        :type: ``int``

        :exception TypeError: If set to anything other than a number or ``None``.
        """
        return self.infinity_settings.get("temperature", None)

    @infinite_fluid_temperature.setter
    def infinite_fluid_temperature(self, value):
        # type: (float) -> None
        if value is None:
            self.infinity_settings.pop("temperature", None)
        elif isinstance(value, (int, float)):
            if not 0 <= value <= 1000:
                warnings.warn(
                    "'infinite_fluid_temperature' ({}) not in range [0, 1000]; "
                    "will be clamped on import".format(value),
                    TemperatureRangeWarning,
                    stacklevel=2,
                )
            self.infinity_settings["temperature"] = int(value)
        else:
            raise TypeError("'temperature' must be an int or None")

    # =========================================================================

    def set_infinite_fluid(
        self, name=None, percentage=0, mode="at-least", temperature=25
    ):
        # type: (str, int, str, float) -> None
        """
        Sets all of the parameters of the infinite fluid at once.

        Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
        anything not in the range ``[0, 1000]``.

        :param name: The name of the fluid to set.
        :param percentage: The percentage full the pipe is.
        :param mode: The mode in which to interact with the fluid. Can be one of
            ``"at-least"``, ``"at-most"``, ``"exactly"``, ``"add"``, or
            ``"remove"``.
        :param temperature: The temperature of the fluid to create.

        :exception TypeError: If any of the argument's types mismatch their
            intended values.
        :exception InvalidFluidError: If ``name`` is not a valid name for a
            fluid.
        :exception InvalidModeError: If ``mode`` is not one of the values
            specified above.
        :exception ValueError: If percentage was set to a negative value.
        """
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
