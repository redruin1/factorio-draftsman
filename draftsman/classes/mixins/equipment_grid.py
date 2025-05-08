# equipment_grid.py

from draftsman.classes.exportable import Exportable
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import EquipmentComponent
from draftsman.validators import and_, instance_of
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    EquipmentID,
    QualityName,
    uint32,
)
from draftsman.warning import EquipmentGridWarning

from draftsman.data import equipment as equipment_data

import attrs
from types import SimpleNamespace
from typing import Optional
import warnings


@attrs.define
class EquipmentGrid:
    id: str = attrs.field()  # TODO: equipment_grid_name

    @property
    def equipment_categories(self) -> list[str]:  # TODO: EquipmentCategoryName
        """
        The list of equipment categories that can live in this entity.
        """
        return equipment_data.grids[self.id]["equipment_categories"]

    @property
    def width(self) -> uint32:
        """
        The width of the equipment grid in tiles.
        """
        # TODO: modulate based on quality
        return equipment_data.grids[self.id]["width"]

    @property
    def height(self) -> uint32:
        """
        The height of the equipment grid in tiles.
        """
        # TODO: modulate based on quality
        return equipment_data.grids[self.id]["height"]

    @property
    def locked(self) -> bool:
        """
        Whether or not this equipment grid is locked from user interaction.
        """
        return equipment_data.grids[self.id].get("locked", False)


# Only store one equipment grid and reuse across every entity
_equipment_grids = {grid: EquipmentGrid(grid) for grid in equipment_data.grids}


@attrs.define(slots=False)
class EquipmentGridMixin(Exportable):  # (RequestItemsMixin)
    """
    Enables the entity to have an equipment grid.
    """

    # class Format(BaseModel):
    #     class EquipmentComponent(DraftsmanBaseModel):
    #         class EquipmentID(DraftsmanBaseModel):
    #             name: str

    #         equipment: EquipmentID = Field(..., description="TODO")
    #         position: IntPosition = Field(
    #             ...,
    #             description="The top leftmost tile in which this item sits, 0-based.",
    #         )

    #     enable_logistics_while_moving: Optional[bool] = Field(  # TODO: optional?
    #         True, description="TODO"
    #     )
    #     grid: list[EquipmentComponent] = Field([], description="TODO")

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
    def equipment_grid(self):
        """
        The equipment grid prototype of this entity. Contains metadata about the
        equipment grid properties associated with this particular entity.
        Returns ``None`` if this entity is not recognized by Draftsman. Read
        only; not exported.
        """
        grid_id = self.prototype.get("equipment_grid", None)
        if grid_id is None:
            return None
        return _equipment_grids.get(grid_id, None)

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

    # @property
    # def allowed_equipment(): # TODO
    #     """
    #     """
    #     return []

    # =========================================================================

    def _equipment_converter(value):
        if isinstance(value, list):
            return [EquipmentComponent.converter(elem) for elem in value]
        return value

    def _ensure_has_equipment_grid(self, attr, value, mode=None):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            if self.equipment_grid is None and value != []:
                msg = "This entity does not have an equipment grid to modify"
                warnings.warn(EquipmentGridWarning(msg))

    equipment: list[EquipmentComponent] = attrs.field(
        factory=list,
        converter=_equipment_converter,
        validator=and_(
            instance_of(list[EquipmentComponent]), _ensure_has_equipment_grid
        ),
    )
    """
    The equipment specification of this particular entity, defining what 
    equipment is requested and where it should live in the 
    :py:attr:`.equipment_grid`.

    .. NOTE::

        This construct specifies where items should live, but on it's own it 
        does nothing; you also need to *request* the items with 
        :py:attr:`.item_requests` in order for robots to actually try to fulfill
        the grid's contents. Alternativly, you can use the helper methods
        :py:meth:`.add_equipment()` and :py:meth:`.remove_equipment()` which
        will take care of this book-keeping for you.
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

    enable_logistics_while_moving: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    Whether or not to attempt to satisfy the logistic requests of this entity
    while it is in motion.
    """

    # =========================================================================

    def add_equipment(
        self, name: str, position: Vector = (0, 0), quality: QualityName = "normal"
    ) -> None:
        """
        Adds a piece of equipment with ``equipment_name`` at ``position``, where
        position is an integer coordinate corresponding to the top-left tile of
        the placed equipment.

        :param equipment_name: The name of the equipment to place in the grid.
        :param position: The integer position with which to place this
            particular piece of equipment. Usually specified as a tuple.
        :param quality: The quality of the equipment to add.
        """
        # TODO
        # Raises :py:warn:`.EquipmentGridWarning` if attempting to place an entity
        # at an invalid position, or such that it overlaps other items in the grid.

        # Add the item to the equipment
        # TODO: does this revalidate?
        self.equipment = self.equipment + [
            EquipmentComponent(
                equipment=EquipmentID(
                    name=name,
                    quality=quality,
                ),
                position=position,
            )
        ]

        # Check to see if we already request this item via item requests
        for item_request in self.item_requests:
            item_request: AttrsItemRequest
            if item_request.id.name == name and item_request.id.quality == quality:
                # Update existing grid_count
                item_request.items.grid_count += 1
                return

        # No existing request found - add new one
        self.item_requests.append(
            AttrsItemRequest(
                id=AttrsItemID(name=name, quality=quality),
                items=AttrsItemSpecification(grid_count=1),
            )
        )

    def remove_equipment(
        self,
        name: Optional[str] = None,
        position: Optional[Vector] = None,
        quality: Optional[QualityName] = None,
    ) -> None:
        """
        Removes all equipment matching the passed in arguments.

        Every time equipment is removed, any item requests associated with it
        are also updated properly. If the item request has no items requested,
        it is removed by the end of this method.

        :param name: The name of the equipment to remove.
        :param position: The top left coordinate of the position to remove the
            equipment from.
        :param quality: The quality of the equipment to remove.
        """
        # Keep track of which equipment we remove so we can update `grid_count`
        removed_equipment = {}

        def test(equipment: EquipmentComponent):
            value = (name, position, quality) != (
                equipment.equipment.name if name else None,
                equipment.position if position else None,
                equipment.equipment.quality if quality else None,
            )

            if not value:
                key = (equipment.equipment.name, equipment.equipment.quality)
                if key not in removed_equipment:
                    removed_equipment[key] = 0
                removed_equipment[key] += 1

            return value

        self.equipment = list(filter(test, self.equipment))

        # Iterate over item requests of the removed equipment and decrement the
        # grid counts of each one
        for item_request in self.item_requests:
            item_request: AttrsItemRequest
            key = (item_request.id.name, item_request.id.quality)
            if key in removed_equipment:
                # Make sure to not underflow, just in case
                item_request.items.grid_count = max(
                    0, item_request.items.grid_count - removed_equipment[key]
                )

        # Strip item requests that are empty (and thus redundant)
        # NOTE: we also have to check the regular item requests (not just
        # `grid_count`); "quickest" way to do that is to just compare with new
        # ItemRequest with just the ID set:
        self.item_requests = [
            request
            for request in self.item_requests
            if request != AttrsItemRequest(id=request.id)
        ]


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:equipment_grid_mixin"},
    EquipmentGridMixin,
    lambda fields: {
        "enable_logistics_while_moving": fields.enable_logistics_while_moving.name,
        "grid": fields.equipment.name,
    },
)
