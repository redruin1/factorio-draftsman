# infinity_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import RequestItemsMixin, InventoryMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.signatures import DraftsmanBaseModel, uint16, uint32

from draftsman.data.entities import infinity_containers
from draftsman.data import items

import copy
from pydantic import ConfigDict, Field, ValidationError
from typing import Any, Literal, Optional, Union


class InfinityContainer(RequestItemsMixin, InventoryMixin, Entity):
    """
    An entity used to create an infinite amount of any item.
    """

    class Format(RequestItemsMixin.Format, InventoryMixin.Format, Entity.Format):
        class InfinitySettings(DraftsmanBaseModel):
            class InfinityFilter(DraftsmanBaseModel):
                index: uint16 = Field(
                    ...,
                    description="""
                    Where in the infinity containers GUI this filter will exist,
                    1-based.
                    """,
                )
                name: str = Field(  # TODO: ItemID
                    ...,
                    description="""
                    The name of the item to create/remove.
                    """,
                )
                count: Optional[uint32] = Field(
                    0,
                    description="""
                    The amount of this item to keep in the entity, as dicerned
                    by 'mode'.
                    """,
                )
                mode: Optional[Literal["at-least", "at-most", "exactly"]] = Field(
                    "at-least",
                    description="""
                    What manner in which to create or remove this item from the 
                    entity. 'at-least' sets 'count' as a lower-bound, 'at-most' 
                    sets 'count' as an upper-bound, and exactly makes the 
                    quantity of this item match 'count' exactly.
                    """,
                )

            filters: Optional[list[InfinityFilter]] = Field(
                [],
                description="""
                The list of items to infinitely create or remove from this 
                entity's inventory.
                """,
            )
            remove_unfiltered_items: Optional[bool] = Field(
                False,
                description="""
                Whether or not items not in the 'filters' object will be removed
                from this entity's inventory.
                """,
            )

        infinity_settings: Optional[InfinitySettings] = InfinitySettings()

        model_config = ConfigDict(title="InfinityContainer")

    def __init__(
        self,
        name: str = infinity_containers[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        items: dict[str, uint32] = {},  # TODO: ItemID
        infinity_settings: Format.InfinitySettings = Format.InfinitySettings(),
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format

        super().__init__(
            name,
            infinity_containers,
            position=position,
            tile_position=tile_position,
            bar=bar,
            items=items,
            tags=tags,
            **kwargs
        )

        self.infinity_settings = infinity_settings

        self.validate_assignment = validate_assignment

        if validate:
            self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def infinity_settings(self) -> Optional[Format.InfinitySettings]:
        """
        The settings that control the manner in which items are spawned or
        removed.

        :getter: Gets the ``infinity_settings`` of the ``InfinityContainer``.
        :setter: Sets the ``infinity_settings`` of the ``InfinityContainer``.
            Defaults to an empty ``dict`` if set to ``None``.
        :type: :py:data:`.INFINITY_CONTAINER`

        :exception DataFormatError: If set to anything that does not match the
            :py:data:`.INFINITY_CONTAINER` format.
        """
        return self._root.infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value: Optional[Format.InfinitySettings]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "infinity_settings", value
            )
            self._root.infinity_settings = result
        else:
            self._root.infinity_settings = value

    # =========================================================================

    @property
    def remove_unfiltered_items(self) -> Optional[bool]:
        """
        Whether or not to remove items that exceed the amounts specified in the
        ``InfinityContainer``'s filters.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.infinity_settings.remove_unfiltered_items

    @remove_unfiltered_items.setter
    def remove_unfiltered_items(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.InfinitySettings,
                self.infinity_settings,
                "remove_unfiltered_items",
                value,
            )
            self.infinity_settings.remove_unfiltered_items = result
        else:
            self.infinity_settings.remove_unfiltered_items = value

    # =========================================================================

    def set_infinity_filter(
        self,
        index: uint16,
        item: Optional[str],
        mode: Literal["at-least", "at-most", "exactly", None] = "at-least",
        count: Optional[uint32] = None,
    ):
        """
        Sets an infinity filter.

        :param index: The index of the filter to set.
        :param name: The name of the item to interact with.
        :param mode: The manner in which to set the filter. Can be one of
            ``"at-least"``, ``"at-most"``, or ``"exactly"``.
        :param count: The amount of the item to request. If set to ``None``, the
            amount set will default to the stack size of ``name``, if name can
            be deduced to a valid item. Otherwise ``count`` will default to 0.
        """

        index = int(index)
        if count is None:
            if item is None:
                count = 0
            else:  # default count to the item's stack size
                count = items.raw.get(item, {}).get("stack_size", 0)

        # Check to see if filters already contains an entry with the same index
        existing_index = False
        for i, filter_entry in enumerate(self.infinity_settings["filters"]):
            if index + 1 == filter_entry["index"]:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.infinity_settings["filters"][i]
                    return
                else:  # Set the new value
                    existing_index = i
                break

        try:
            new_filter = self.Format.InfinitySettings.InfinityFilter(
                index=index + 1,
                name=item,
                count=count,
                mode=mode,
            )
        except ValidationError as e:
            raise DataFormatError(e) from None

        if existing_index is not False:
            self.infinity_settings["filters"][existing_index] = new_filter
        else:  # No entry with the same index was found
            self.infinity_settings["filters"].append(new_filter)

    def merge(self, other):
        super().merge(other)

        self.infinity_settings = copy.deepcopy(other.infinity_settings)

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and self.infinity_settings == other.infinity_settings
        )
