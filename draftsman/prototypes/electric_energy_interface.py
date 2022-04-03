# electric_energy_interface.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes import Entity
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import electric_energy_interfaces

import warnings


class ElectricEnergyInterface(Entity):
    def __init__(self, name=electric_energy_interfaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(ElectricEnergyInterface, self).__init__(
            name, electric_energy_interfaces, **kwargs
        )

        self.buffer_size = None  # TODO: default
        if "buffer_size" in kwargs:
            self.buffer_size = kwargs["buffer_size"]
            self.unused_args.pop("buffer_size")
        self._add_export("buffer_size", lambda x: x is not None)

        self.power_production = None  # TODO: default
        if "power_production" in kwargs:
            self.power_production = kwargs["power_production"]
            self.unused_args.pop("power_production")
        self._add_export("power_production", lambda x: x is not None)

        self.power_usage = None  # TODO: default
        if "power_usage" in kwargs:
            self.power_usage = kwargs["power_usage"]
            self.unused_args.pop("power_usage")
        self._add_export("power_usage", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def buffer_size(self):
        # type: () -> int
        """
        TODO
        """
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        # type: (int) -> None
        if value is None or isinstance(value, int):
            self._buffer_size = value
        else:
            raise TypeError("'buffer_size' must be an int or None")

    # =========================================================================

    @property
    def power_production(self):
        # type: () -> int
        """
        TODO
        """
        return self._power_production

    @power_production.setter
    def power_production(self, value):
        # type: (int) -> None
        if value is None or isinstance(value, int):
            self._power_production = value
        else:
            raise TypeError("'power_production' must be an int or None")

    # =========================================================================

    @property
    def power_usage(self):
        # type: () -> int
        """
        TODO
        """
        return self._power_usage

    @power_usage.setter
    def power_usage(self, value):
        # type: (int) -> None
        if value is None or isinstance(value, int):
            self._power_usage = value
        else:
            raise TypeError("'power_usage' must be an int or None")