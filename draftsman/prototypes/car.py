# car.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    RequestItemsMixin,
    # EquipmentGridMixin,
    OrientationMixin
)
from draftsman.classes.vector import Vector, PrimitiveVector, PrimitiveIntVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import DraftsmanBaseModel, IntPosition, uint32
from draftsman.utils import get_first

from draftsman.data import entities
from draftsman.data.entities import cars

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Car(RequestItemsMixin, OrientationMixin, Entity):
    """
    A drivable entity which uses wheels or tracks for locomotion.
    """
    class Format(
        RequestItemsMixin.Format,
        OrientationMixin.Format,
        Entity.Format
    ):
        class EquipmentComponent(DraftsmanBaseModel):
            class EquipmentID(DraftsmanBaseModel):
                name: str

            equipment: EquipmentID = Field(
                ...,
                description="TODO"
            )
            position: IntPosition = Field(
                ...,
                description="The top leftmost tile in which this item sits, 0-based."
            )

        enable_logistics_while_moving: Optional[bool] = Field(  # TODO: optional?
            True,
            description="TODO"
        )
        grid: list[EquipmentComponent] = Field(
            [],
            description="TODO"
        )
        trunk_inventory: None = None # TODO: what is this?
        ammo_inventory: None = None # TODO: what is this?
        driver_is_main_gunner: Optional[bool] = Field( #TODO: optional?
            True,
            description="Whether or not the driver controls this entity's weapons.",
        )
        selected_gun_index: Optional[uint32] = Field( # TODO: size, optional?
            1,
            description="Which gun is currently selected, if there are multiple guns to select from. 1-indexed."
        )

        model_config = ConfigDict(title="Car")

    # =========================================================================

    def __init__(
        self,
        name: Optional[str] = get_first(cars),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Optional[Orientation] = Orientation.NORTH,
        enable_logistics_while_moving: Optional[bool] = True,
        grid: list[Format.EquipmentComponent] = [],
        trunk_inventory = None,
        ammo_inventory = None,
        driver_is_main_gunner: Optional[bool] = True,
        selected_gun_index: Optional[uint32] = 1, # TODO: size
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        super().__init__(
            name,
            cars,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            items=items,
            tags=tags,
            **kwargs
        )

        self.enable_logistics_while_moving = enable_logistics_while_moving
        self.grid = grid # TODO: should be moved to mixin
        # self.trunk_inventory = trunk_inventory
        # self.ammo_inventory = ammo_inventory
        self.driver_is_main_gunner = driver_is_main_gunner
        self.selected_gun_index = selected_gun_index

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def has_equipment_grid(self) -> bool:
        """
        Determines whether or not this entity has a modifiable equipment grid.
        If not, any attempts to set the equipment grid will have no resultant
        effect when imported into Factorio. Read only.

        TODO
        """
        return "equipment_grid" in entities.raw[self.name]
    
    # =========================================================================

    @property
    def enable_logistics_while_moving(self) -> Optional[bool]:
        """
        TODO
        """
        return self._root.enable_logistics_while_moving
    
    @enable_logistics_while_moving.setter
    def enable_logistics_while_moving(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "enable_logistics_while_moving", value
            )
            self._root.enable_logistics_while_moving = result
        else:
            self._root.enable_logistics_while_moving = value

    # =========================================================================

    @property
    def equipment_grid(self) -> Optional[bool]:
        """
        TODO
        """
        return self._root.grid
    
    @equipment_grid.setter
    def equipment_grid(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "grid", value
            )
            self._root.grid = result
        else:
            self._root.grid = value

    # =========================================================================

    @property
    def trunk_inventory(self) -> None:
        """
        TODO
        """
        return self._root.trunk_inventory
    
    # =========================================================================

    @property
    def ammo_inventory(self) -> None:
        """
        TODO
        """
        return self._root.trunk_inventory
    
    # =========================================================================

    @property
    def driver_is_main_gunner(self) -> Optional[bool]:
        """
        TODO
        """
        return self._root.driver_is_main_gunner
    
    @driver_is_main_gunner.setter
    def driver_is_main_gunner(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "driver_is_main_gunner", value
            )
            self._root.driver_is_main_gunner = result
        else:
            self._root.driver_is_main_gunner = value

    # =========================================================================

    @property
    def selected_gun_index(self) -> Optional[uint32]:
        """
        TODO
        """
        return self._root.selected_gun_index
    
    @selected_gun_index.setter
    def selected_gun_index(self, value: Optional[uint32]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "selected_gun_index", value
            )
            self._root.selected_gun_index = result
        else:
            self._root.selected_gun_index = value

    # =========================================================================

    def add_equipment(equipment_name, position: PrimitiveIntVector) -> None:
        pass # TODO

    def remove_equipment(equipment_name, position: Optional[PrimitiveIntVector]=None) -> None:
        pass # TODO

    
