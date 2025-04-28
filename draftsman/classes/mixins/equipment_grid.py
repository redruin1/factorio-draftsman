# equipment_grid.py

from draftsman.classes.exportable import Exportable, attempt_and_reissue
from draftsman.classes.vector import PrimitiveIntVector
from draftsman.serialization import draftsman_converters
from draftsman.signatures import EquipmentComponent
from draftsman.validators import instance_of
from draftsman.signatures import DraftsmanBaseModel, IntPosition

from draftsman.data import entities

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
class EquipmentGridMixin(Exportable):
    """
    Enables the entity to have an equipment grid.
    """

    class Format(BaseModel):
        class EquipmentComponent(DraftsmanBaseModel):
            class EquipmentID(DraftsmanBaseModel):
                name: str

            equipment: EquipmentID = Field(..., description="TODO")
            position: IntPosition = Field(
                ...,
                description="The top leftmost tile in which this item sits, 0-based.",
            )

        enable_logistics_while_moving: Optional[bool] = Field(  # TODO: optional?
            True, description="TODO"
        )
        grid: list[EquipmentComponent] = Field([], description="TODO")

    # =========================================================================

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.enable_logistics_while_moving = kwargs.get(
    #         "enable_logistics_while_moving", None
    #     )
    #     self.grid = kwargs.get("grid", None)

    # =========================================================================

    @property
    def has_equipment_grid(self) -> bool:
        """
        Determines whether or not this entity has a modifiable equipment grid.
        If not, any attempts to set the equipment grid will have no resultant
        effect when imported into Factorio. Not exported; read only.
        """
        return "equipment_grid" in self.prototype

    # =========================================================================

    enable_logistics_while_moving: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    Whether or not to attempt to satisfy the logistic requests of this entity
    while it is in motion.
    """

    # @property
    # def enable_logistics_while_moving(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self._root.enable_logistics_while_moving

    # @enable_logistics_while_moving.setter
    # def enable_logistics_while_moving(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "enable_logistics_while_moving",
    #             value,
    #         )
    #         self._root.enable_logistics_while_moving = result
    #     else:
    #         self._root.enable_logistics_while_moving = value

    # =========================================================================

    def _equipment_grid_converter(value):
        if isinstance(value, list):
            return [EquipmentComponent(**elem) for elem in value]
        return value

    equipment_grid: list[EquipmentComponent] = attrs.field(
        factory=list,
        converter=_equipment_grid_converter,
        validator=instance_of(list),  # TODO: validators
    )
    """
    TODO
    """

    # @property
    # def equipment_grid(self) -> Optional[bool]: # TODO: implement
    #     """
    #     TODO
    #     """
    #     return self._root.grid

    # @equipment_grid.setter
    # def equipment_grid(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "grid", value
    #         )
    #         self._root.grid = result
    #     else:
    #         self._root.grid = value

    # =========================================================================

    def add_equipment(self, equipment_name: str, position: PrimitiveIntVector) -> None:
        pass  # TODO

    def remove_equipment(
        self, equipment_name: str, position: Optional[PrimitiveIntVector] = None
    ) -> None:
        pass  # TODO


draftsman_converters.add_schema(
    {"$id": "factorio:equipment_grid_mixin"},
    EquipmentGridMixin,
    lambda fields: {
        "enable_logistics_while_moving": fields.enable_logistics_while_moving.name,
        "grid": fields.equipment_grid.name,
    },
)
