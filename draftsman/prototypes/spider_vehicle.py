# spider_vehicle.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    RequestItemsMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import DraftsmanBaseModel, Section, uint32
from draftsman.utils import Vector, PrimitiveVector, get_first

from draftsman.data.entities import spider_vehicles

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class SpiderVehicle(
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    RequestItemsMixin,
    OrientationMixin,
    Entity,
):
    """
    A drivable entity which uses legs for locomotion.
    """

    class Format(
        VehicleMixin.Format,
        EquipmentGridMixin.Format,
        RequestFiltersMixin.Format,
        RequestItemsMixin.Format,
        OrientationMixin.Format,
        Entity.Format,
    ):
        class AutoTargetParameters(DraftsmanBaseModel):
            auto_target_without_gunner: bool = Field(
                True, description="Auto targets when gunner is not present."
            )
            auto_target_with_gunner: bool = Field(
                False, description="Auto targets when gunner is present."
            )

        automatic_targeting_parameters: Optional[
            AutoTargetParameters
        ] = AutoTargetParameters()

        class RequestFilters(DraftsmanBaseModel):
            sections: Optional[list[Section]] = Field(
                [], description="""The logistics groups requested to this spidertron."""
            )
            trash_not_requested: Optional[bool] = Field(
                False,
                description="""Moves any unrequested item to trash slots if enabled.""",
            )
            request_from_buffers: Optional[bool] = Field(
                True,
                description="""Whether or not to request from buffer chests. Always true.""",
            )
            enabled: Optional[bool] = Field(
                True,
                description="""Master switch to enable/disble logistics requests to this spidertron.""",
            )

        request_filters: RequestFilters = RequestFilters()

        model_config = ConfigDict(title="SpiderVehicle")

    # =========================================================================

    def __init__(
        self,
        name: Optional[str] = get_first(spider_vehicles),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Optional[Orientation] = Orientation.NORTH,
        enable_logistics_while_moving: Optional[bool] = True,
        grid: list[Format.EquipmentComponent] = [],
        trunk_inventory=None,
        ammo_inventory=None,
        driver_is_main_gunner: Optional[bool] = True,
        selected_gun_index: Optional[uint32] = 1,  # TODO: size
        automatic_targeting_parameters: Format.AutoTargetParameters = {},
        request_filters: Format.RequestFilters = {},
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """
        super().__init__(
            name,
            spider_vehicles,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            enable_logistics_while_moving=enable_logistics_while_moving,
            grid=grid,
            trunk_inventory=trunk_inventory,
            ammo_inventory=ammo_inventory,
            driver_is_main_gunner=driver_is_main_gunner,
            selected_gun_index=selected_gun_index,
            items=items,
            tags=tags,
            **kwargs
        )

        self.automatic_targeting_parameters = automatic_targeting_parameters
        self.request_filters = request_filters

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def automatic_targeting_parameters(self) -> Optional[Format.AutoTargetParameters]:
        """
        TODO
        """
        return self._root.automatic_targeting_parameters

    @automatic_targeting_parameters.setter
    def automatic_targeting_parameters(
        self, value: Optional[Format.AutoTargetParameters]
    ):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "automatic_targeting_parameters",
                value,
            )
            self._root.automatic_targeting_parameters = result
        else:
            self._root.automatic_targeting_parameters = value

    # =========================================================================

    @property
    def auto_target_without_gunner(self) -> Optional[bool]:
        """
        TODO
        """
        return self.automatic_targeting_parameters.auto_target_without_gunner

    @auto_target_without_gunner.setter
    def auto_target_without_gunner(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AutoTargetParameters,
                self.automatic_targeting_parameters,
                "auto_target_without_gunner",
                value,
            )
            self.automatic_targeting_parameters.auto_target_without_gunner = result
        else:
            self.automatic_targeting_parameters.auto_target_without_gunner = value

    # =========================================================================

    @property
    def auto_target_with_gunner(self) -> Optional[bool]:
        """
        TODO
        """
        return self.automatic_targeting_parameters.auto_target_with_gunner

    @auto_target_with_gunner.setter
    def auto_target_with_gunner(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AutoTargetParameters,
                self.automatic_targeting_parameters,
                "auto_target_with_gunner",
                value,
            )
            self.automatic_targeting_parameters.auto_target_with_gunner = result
        else:
            self.automatic_targeting_parameters.auto_target_with_gunner = value

    # =========================================================================

    __hash__ = Entity.__hash__
