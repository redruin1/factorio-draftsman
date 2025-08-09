# energy_source.py

from draftsman.signatures import uint16

from draftsman.data import entities, items

import attrs
from typing import Optional


@attrs.define(slots=False)
class EnergySourceMixin:
    """
    Entities which inherit this mixin consume a specific kind of energy. This
    class populates methods depending on what type of energy source is
    configured for a particular entity.
    """

    @property
    def energy_source(self) -> Optional[dict]:
        """
        The energy source specification for this entity. Returns ``None`` if
        this entity is not recognized by the current environment.

        .. seealso::

            https://lua-api.factorio.com/latest/types/BaseEnergySource.html.
        """
        return self.prototype.get("energy_source", None)

    # =========================================================================
    # BurnerEnergySource
    # =========================================================================

    @property
    def fuel_input_size(self) -> uint16 | None:
        """
        Gets the total number of fuel input slots that this entity can hold.
        Returns ``None`` if :py:attr:`.energy_source` is not of type "burner", 
        or if the name of this entity is not recognized in the current 
        environment.
        """
        if self.energy_source is not None:
            return self.energy_source.get("fuel_inventory_size", 0)
        else:
            return None

    # =========================================================================

    @property
    def fuel_output_size(self) -> uint16 | None:
        """
        Gets the total number of fuel output slots that this entity has. Returns
        ``None`` if :py:attr:`.energy_source` is not of type "burner", or if the
        entity itself is not recognized in the current environment.
        """
        if self.energy_source is not None:
            return self.energy_source.get("burnt_inventory_size", 0)
        else:
            return None

    # =========================================================================

    @property  # cache?
    def allowed_fuel_items(self) -> Optional[set[str]]:
        """
        A set of strings, each one a valid item that can be used as a fuel
        source to power this entity. If :py:attr:`.energy_source` is not of type
        "burner", then this property returns an empty set. Returns ``None`` if 
        this entity is not recognized by the current environment.
        """
        if self.name not in entities.raw:
            return None
        if self.energy_source is None or self.energy_source["type"] != "burner":
            return set()

        # Fuel types can be specified either as a "categories" list or as a
        # single "category"
        if "fuel_categories" in self.energy_source:
            fuel_categories = self.energy_source["fuel_categories"]
        else:
            # Factorio 1.0 only
            fuel_categories = [self.energy_source.get("fuel_category", "chemical")]

        result = set()
        for fuel_category in fuel_categories:
            result.update(items.fuels[fuel_category])
        return result
