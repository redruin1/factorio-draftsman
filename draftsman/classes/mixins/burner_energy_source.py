# burner_energy_source.py

from draftsman.constants import ValidationMode
from draftsman.signatures import ItemName, uint16, uint32
from draftsman.warning import FuelCapacityWarning, FuelLimitationWarning

from draftsman.data import entities, items

import math
from pydantic import BaseModel, ValidationInfo, field_validator
from typing import Optional

_valid_fuel_items: dict[str, set[str]] = {}

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from draftsman.classes.mixins import RequestItemsMixin


class BurnerEnergySourceMixin:  # (RequestItemsMixin)
    """
    Allows this entity to own a fuel input slot or slots and accept fuel item
    requests (for categories available to the specific entity). Implicitly
    inherits :py:class:`~.RequestItemsMixin`.
    """

    class Format(BaseModel):
        @field_validator("items", check_fields=False)
        @classmethod
        def ensure_fuel_type_valid(
            cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        ):
            """
            Warn the user if they set a fuel item that is disallowed for this
            particular entity.
            """
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "BurnerEnergySourceMixin" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            if entity.allowed_fuel_items is None:  # entity not recognized
                return value

            for item in entity.fuel_items:
                if item["id"]["name"] not in entity.allowed_fuel_items:
                    if len(entity.allowed_fuel_items) == 0:
                        context_string = " this entity does not consume items for power"
                    else:
                        context_string = (
                            " the valid fuel items for this entity are {}".format(
                                entity.allowed_fuel_items
                            )
                        )

                    warning_list.append(
                        FuelLimitationWarning(
                            "Cannot add fuel item '{}' to '{}';{}".format(
                                item["id"]["name"], entity.name, context_string
                            )
                        )
                    )

            return value

        # @field_validator("items", check_fields=False)
        # @classmethod
        # def ensure_fuel_doesnt_exceed_slots( # TODO: reimplement
        #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        # ):
        #     """
        #     Warn the user if they request valid burnable fuel, but the amount
        #     they request will exceed the number if internal fuel slots for this
        #     entity.
        #     """
        #     if not info.context or value is None:
        #         return value
        #     if info.context["mode"] <= ValidationMode.MINIMUM:
        #         return value

        #     entity: "BurnerEnergySourceMixin" = info.context["object"]
        #     warning_list: list = info.context["warning_list"]

        #     if entity.total_fuel_slots is None:  # entity not recognized
        #         return value

        #     if entity.fuel_slots_occupied > entity.total_fuel_slots:
        #         issue = FuelCapacityWarning(
        #             "Amount of slots occupied by fuel items ({}) exceeds available fuel slots ({}) for entity '{}'".format(
        #                 entity.fuel_slots_occupied, entity.total_fuel_slots, entity.name
        #             )
        #         )

        #         warning_list.append(issue)

        #     return value

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        # Cache a set of valid fuel items for this entity, if they have not been
        # created beforehand
        # We do this before calling super in case `items` has been set as a
        # keyword argument and needs to be validated

        super().__init__(name, similar_entities, **kwargs)

        if name not in _valid_fuel_items:
            if name in entities.raw:
                energy_source = self.input_energy_source
                if energy_source is not None:
                    if "fuel_categories" in energy_source:
                        fuel_categories = energy_source[
                            "fuel_categories"
                        ]  # pragma: no coverage
                    else:
                        fuel_categories = [
                            energy_source.get("fuel_category", "chemical")
                        ]

                    _valid_fuel_items[name] = set()
                    for fuel_category in fuel_categories:
                        _valid_fuel_items[name].update(items.fuels[fuel_category])
                else:
                    _valid_fuel_items[name] = set()
            else:
                _valid_fuel_items[name] = None

    # =========================================================================

    @property
    def input_energy_source(self) -> Optional[dict]:
        """
        TODO
        """
        energy_source = entities.raw.get(self.name, {"energy_source": None})[
            "energy_source"
        ]
        if energy_source is not None and energy_source["type"] == "burner":
            return energy_source
        else:
            return None

    # =========================================================================

    @property
    def total_fuel_slots(self) -> Optional[uint16]:
        """
        Gets the total number of fuel input slots that this entity can hold.
        Returns ``None`` if the name of this entity is not recognized by
        Draftsman. Not exported; read only.
        """
        energy_source = self.input_energy_source
        if energy_source is not None:
            return energy_source.get("fuel_inventory_size", None)
        else:
            return None

    # =========================================================================

    # @property
    # def fuel_slots_occupied(self) -> int: # TODO: reimplment
    #     """
    #     Gets the total number of fuel slots currently occupied by fuel item
    #     requests. Items not recognized by Draftsman are ignored from the
    #     returned count.
    #     """
    #     return sum(
    #         int(math.ceil(count / float(items.raw[item]["stack_size"])))
    #         for item, count in self.fuel_items
    #         if item in items.raw
    #     )

    # =========================================================================

    @property
    def allowed_fuel_items(self) -> Optional[set[str]]:
        """
        A set of strings, each one a valid item that can be used as a fuel
        source to power this furnace. If this furnace does not burn items to
        fuel itself (and instead uses electricity, fluid, etc.) then this
        property returns an empty set. Returns ``None`` if this entity is not
        recognized by Draftsman. Not exported; read only.
        """
        return _valid_fuel_items.get(self.name, None)

    # =========================================================================

    @property
    def fuel_items(self) -> list["RequestItemsMixin.Format.ItemRequest"]:
        """
        The subset of :py:attr:`.items` where each key is a valid item fuel
        source that can be consumed by this entity. Returns an empty dict if
        none of the keys of ``items`` are known as valid module names. Not
        exported; read only.
        """
        return [item for item in self.items if item["id"]["name"] in items.all_fuel_items]
