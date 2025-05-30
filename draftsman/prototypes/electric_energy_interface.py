# electric_energy_interface.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin
from draftsman.serialization import draftsman_converters
from draftsman.utils import parse_energy
from draftsman.validators import instance_of, try_convert

from draftsman.data.entities import electric_energy_interfaces
from draftsman.data import entities

import attrs
from typing import Optional


@attrs.define
class ElectricEnergyInterface(EnergySourceMixin, Entity):
    """
    An entity that interfaces with an electrical grid.
    """

    @property
    def similar_entities(self) -> list[str]:
        return electric_energy_interfaces

    # =========================================================================

    @property
    def default_buffer_size(self) -> Optional[float]:
        """
        TODO
        """
        energy_string = (
            entities.raw.get(self.name, {})
            .get("energy_source", {})
            .get("buffer_capacity", None)
        )
        if energy_string is None:
            return None
        else:
            return parse_energy(energy_string)

    # =========================================================================

    @property
    def default_power_production(self) -> Optional[float]:
        """
        TODO
        """
        energy_string = entities.raw.get(self.name, {}).get("energy_production", None)
        if energy_string is None:
            return None
        else:
            return parse_energy(energy_string)

    # =========================================================================

    @property
    def default_power_usage(self) -> Optional[float]:
        """
        TODO
        """
        energy_string = entities.raw.get(self.name, {}).get("energy_usage", None)
        if energy_string is None:
            return None
        else:
            return parse_energy(energy_string)

    # =========================================================================

    buffer_size: float = attrs.field(
        converter=try_convert(float), validator=instance_of(float)
    )
    """
    The amount of electrical energy stored in this entity in Watts.

    :getter: Gets the value of the buffer.
    :setter: Sets the value of the buffer.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    """

    @buffer_size.default
    def _(self):
        default = self.default_buffer_size
        return 0.0 if default is None else default

    # =========================================================================

    power_production: float = attrs.field(
        converter=try_convert(float), validator=instance_of(float)
    )
    """
    The amount of electrical energy to create each tick in Watts.

    :getter: Gets how much to make.
    :setter: Sets how much to make.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    """

    @power_production.default
    def _(self):
        default = self.default_power_production
        return 0.0 if default is None else default

    # =========================================================================

    power_usage: float = attrs.field(
        converter=try_convert(float), validator=instance_of(float)
    )
    """
    The amount of electrical energy to use each tick in Watts.

    :getter: Gets how much to use.
    :setter: Sets how much to use.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    """

    @power_usage.default
    def _(self):
        default = self.default_power_usage
        return 0.0 if default is None else default

    # =========================================================================

    def merge(self, other: "ElectricEnergyInterface"):
        super().merge(other)

        self.buffer_size = other.buffer_size
        self.power_production = other.power_production
        self.power_usage = other.power_usage

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    ElectricEnergyInterface,
    lambda fields: {
        fields.buffer_size.name: "buffer_size",
        fields.power_production.name: "power_production",
        fields.power_usage.name: "power_usage",
    },
)
