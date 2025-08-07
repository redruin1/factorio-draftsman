# electric_energy_interface.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin
from draftsman.serialization import draftsman_converters
from draftsman.utils import parse_energy, fix_incorrect_pre_init
from draftsman.validators import instance_of, try_convert

from draftsman.data.entities import electric_energy_interfaces
from draftsman.data import entities

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class ElectricEnergyInterface(EnergySourceMixin, DirectionalMixin, Entity):
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
        The default amount of energy (in Joules) this entity can store.
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
        The default amount of energy (in Joules / tick) this entity produces.
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
        The default amount of energy (in Joules / tick) this entity consumes.
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
    The amount of electrical energy that can be stored in this entity in Joules.
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
    The amount of electrical energy to create each tick in Joules.
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
    The amount of electrical energy to use each tick in Joules.
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
