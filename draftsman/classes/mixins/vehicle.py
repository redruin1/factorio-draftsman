# vehicle.py

from draftsman.serialization import instance_of
from draftsman.signatures import uint32

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
class VehicleMixin:
    """
    A number of common properties that all vehicles have.
    """

    # class Format(BaseModel):
    #     trunk_inventory: None = None  # TODO: what is this?
    #     ammo_inventory: None = None  # TODO: what is this?
    #     driver_is_main_gunner: Optional[bool] = Field(  # TODO: optional?
    #         True,
    #         description="Whether or not the driver controls this entity's weapons.",
    #     )
    #     selected_gun_index: Optional[uint32] = Field(  # TODO: size, optional?
    #         1,
    #         description="Which gun is currently selected, if there are multiple guns to select from. 1-indexed.",
    #     )

    # # =========================================================================

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     # self.trunk_inventory = kwargs.get("trunk_inventory", None)
    #     # self.ammo_inventory = kwargs.get("ammo_inventory", None)
    #     self.driver_is_main_gunner = kwargs.get("driver_is_main_gunner", None)
    #     self.selected_gun_index = kwargs.get("selected_gun_index", None)

    # =========================================================================

    trunk_inventory = attrs.field(
        default=None,
    )
    """
    TODO
    """

    # @property
    # def trunk_inventory(self) -> None:
    #     """
    #     TODO
    #     """
    #     return None

    # =========================================================================

    ammo_inventory = attrs.field(
        default=None,
    )
    """
    TODO
    """

    # @property
    # def ammo_inventory(self) -> None:
    #     """
    #     TODO
    #     """
    #     return None

    # =========================================================================

    driver_is_main_gunner: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the driver or the passenger has control of the vehicle's 
    weapons.
    """

    # @property
    # def driver_is_main_gunner(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self._root.driver_is_main_gunner

    # @driver_is_main_gunner.setter
    # def driver_is_main_gunner(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "driver_is_main_gunner", value
    #         )
    #         self._root.driver_is_main_gunner = result
    #     else:
    #         self._root.driver_is_main_gunner = value

    # =========================================================================

    selected_gun_index: uint32 = attrs.field(default=1, validator=instance_of(uint32))
    """
    Which gun is currently selected by the gunner. Defaults to ``1`` for 
    vehicles with only one gun.
    """

    # @property
    # def selected_gun_index(self) -> Optional[uint32]:
    #     """
    #     TODO
    #     """
    #     return self._root.selected_gun_index

    # @selected_gun_index.setter
    # def selected_gun_index(self, value: Optional[uint32]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "selected_gun_index", value
    #         )
    #         self._root.selected_gun_index = result
    #     else:
    #         self._root.selected_gun_index = value
