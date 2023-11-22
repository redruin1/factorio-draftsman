# input_ingredients.py

from draftsman.constants import ValidationMode
from draftsman.signatures import uint32
from draftsman.warning import ItemLimitationWarning

from pydantic import BaseModel, ValidationInfo, field_validator
from typing import Optional


class InputIngredientsMixin:
    class Format(BaseModel):
        @field_validator("items", check_fields=False)
        @classmethod
        def ensure_in_allowed_ingredients(
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

            entity: "InputIngredientsMixin" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            if entity.allowed_input_ingredients is None:  # entity not recognized
                return value

            for item in entity.items:
                # Skip these cases so we can issue better warnings elsewhere
                if item in entity.allowed_modules:
                    continue
                if item not in entity.allowed_input_ingredients:
                    warning_list.append(
                        ItemLimitationWarning(
                            "Cannot request item '{}' to '{}'; this recipe cannot consume it".format(
                                item, entity.name
                            )
                        )
                    )

            return value

        # @field_validator("items", check_fields=False)
        # @classmethod
        # def ensure_fuel_doesnt_exceed_slots(
        #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        # ):
        #     """
        #     Warn the user if they request valid burnable fuel, but the amount
        #     they request will exceed the number if internal fuel slots for this
        #     entity.
        #     """
        #     if not info.context or value is None:
        #         return value
        #     if info.context["mode"] is ValidationMode.MINIMUM:
        #         return value

        #     entity: "InputIngredientsMixin" = info.context["entity"]
        #     warning_list: list = info.context["warning_list"]

        #     if entity.total_fuel_slots is None:  # entity not recognized
        #         return value

        #     if entity.occupied_fuel_slots > entity.total_fuel_slots:
        #         issue = ItemCapacityWarning(
        #             "Amount of slots occupied by current fuel requested ({}) exceeds available fuel slots ({}) for entity '{}'".format(
        #                 entity.occupied_fuel_slots, entity.total_fuel_slots, entity.name
        #             )
        #         )

        #         warning_list.append(issue)

        #     return value
        pass

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        super().__init__(name, similar_entities, **kwargs)

    # @property
    # def allowed_input_ingredients(self) -> set[str]:
    #     """
    #     Gets the list of items that are valid inputs ingredients for crafting
    #     machines of all types. Returns ``None`` if this entity's name is not
    #     recognized by Draftsman. Not exported; read only.
    #     """
    #     return set()

    @property
    def ingredient_items(self):
        """
        The subset of :py:attr:`.items` where each key is a valid input
        ingredient that can be consumed by this entity. Returns an empty dict if
        this entity consumes no ingredients, or what ingredients this entity
        consumes cannot be deduced with the current data configuration. Not
        exported; read only.
        """
        return {
            k: v for k, v in self.items.items() if k in self.allowed_input_ingredients
        }
