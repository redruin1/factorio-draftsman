# electric_energy_interface.py

from draftsman.prototypes.mixins import Entity
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import electric_energy_interfaces

import warnings


class ElectricEnergyInterface(Entity):
    def __init__(self, name = electric_energy_interfaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(ElectricEnergyInterface, self).__init__(
            name, electric_energy_interfaces, **kwargs
        )

        self.buffer_size = None # TODO: default
        if "buffer_size" in kwargs:
            self.set_buffer_size(kwargs["buffer_size"])
            self.unused_args.pop("buffer_size")
        self._add_export("buffer_size", lambda x: x is not None)

        self.power_production = None # TODO: default
        if "power_production" in kwargs:
            self.set_power_production(kwargs["power_production"])
            self.unused_args.pop("power_production")
        self._add_export("power_production", lambda x: x is not None)

        self.power_usage = None # TODO: default
        if "power_usage" in kwargs:
            self.set_power_usage(kwargs["power_usage"])
            self.unused_args.pop("power_usage")
        self._add_export("power_usage", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_buffer_size(self, amount):
        # type: (int) -> None
        """
        """
        self.buffer_size = signatures.INTEGER.validate(amount)

    def set_power_production(self, amount):
        # type: (int) -> None
        """
        """
        self.power_production = signatures.INTEGER.validate(amount)

    def set_power_usage(self, amount):
        # type: (int) -> None
        """
        """
        self.power_usage = signatures.INTEGER.validate(amount)