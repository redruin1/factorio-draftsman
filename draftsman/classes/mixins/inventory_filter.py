# inventory_filter.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import entities
from draftsman.data import items
from draftsman.error import (
    InvalidItemError,
    DataFormatError,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    DraftsmanBaseModel,
    ItemFilter,
    AttrsItemFilter,
    ItemName,
    QualityName,
    Comparator,
    int64,
    uint16,
    ensure_bar_less_than_inventory_size,
)
from draftsman.validators import and_, instance_of

import attrs
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ValidationInfo,
    validate_call,
    field_validator,
)
from typing import Any, Literal, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class InventoryFilterMixin:  # TODO: rename to `FilteredInventoryMixin`
    """
    Allows an Entity to set inventory filters. Only used on :py:class:`.CargoWagon`.
    """

    class Format(BaseModel):
        class InventoryFilters(DraftsmanBaseModel):
            filters: Optional[list[ItemFilter]] = Field(
                None,
                description="""
                Any reserved item filter slots in the container's inventory.
                """,
            )
            bar: Optional[uint16] = Field(
                None,
                description="""
                Limiting bar on this container's inventory.
                """,
            )

            @field_validator("filters", mode="before")
            @classmethod
            def normalize_validate(cls, value: Any):
                if isinstance(value, (list, tuple)):
                    result = []
                    for i, entry in enumerate(value):
                        if isinstance(entry, str):
                            result.append({"index": i + 1, "name": entry})
                        else:
                            result.append(entry)
                    return result
                else:
                    return value

            @field_validator("bar")
            @classmethod
            def ensure_less_than_inventory_size(
                cls, bar: Optional[uint16], info: ValidationInfo
            ):
                return ensure_bar_less_than_inventory_size(cls, bar, info)

        inventory: Optional[InventoryFilters] = Field(
            InventoryFilters(),
            description="""
            Custom inventory object just for cargo wagons. Note that this 
            contains the 'bar' key for this entity type specifically, which 
            differs from all other containers.
            """,
        )

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.inventory = kwargs.get("inventory", self.Format.InventoryFilters())

    # =========================================================================

    @property
    def inventory_size(self) -> Optional[uint16]:
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return entities.raw.get(self.name, {"inventory_size": None})["inventory_size"]

    # =========================================================================

    # @property
    # def inventory(self) -> Format.InventoryFilters:
    #     """
    #     Inventory filter object. Contains the filter information under the
    #     ``"filters"`` key and the inventory limiting bar under the ``"bar"`` key.

    #     This attribute is in the following format::

    #         {
    #             "bar": int,
    #             "filters": [
    #                 {"index": int, "signal": {"name": str, "type": str}},
    #                 ...
    #             ]
    #         }

    #     :getter: Gets the value of the Entity's ``inventory`` object.
    #     :setter: Sets the value of the Entity's ``inventory`` object. Defaults
    #         to an empty ``dict`` if set to ``None``.

    #     :exception DataFormatError: If the set value differs from the
    #         ``INVENTORY_FILTER`` specification.
    #     """
    #     return self._root.inventory

    # @inventory.setter
    # def inventory(self, value: Format.InventoryFilters):
    #     test_replace_me(
    #         self,
    #         type(self).Format,
    #         self._root,
    #         "inventory",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     value = attempt_and_reissue(
    #     #         self, type(self).Format, self._root, "inventory", value
    #     #     )

    #     # if value is None:
    #     #     self._root.inventory = __class__.Format.InventoryFilters()
    #     # else:
    #     #     self._root.inventory = value

    # =========================================================================

    @property
    def filter_count(self) -> Optional[uint16]:
        """
        The number of filter slots that this entity has. In this case, is
        equivalent to the number of inventory slots of the CargoWagon. Returns
        ``None`` if this entity's name is not recognized by Draftsman. Not
        exported; read only.
        """
        return self.inventory_size

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    value[i] = AttrsItemFilter(index=i, name=elem)
                else:
                    value[i] = AttrsItemFilter.converter(elem)
        return value

    filters: list[AttrsItemFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list),  # TODO: validators
    )
    """
    TODO
    """

    # @property
    # def filters(self) -> Optional[list[ItemFilter]]:
    #     """
    #     TODO
    #     """
    #     return self.inventory.filters

    # @filters.setter
    # def filters(self, value: Optional[list[ItemFilter]]):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InventoryFilters,
    #         self.inventory,
    #         "filters",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         __class__.Format.InventoryFilters,
    #     #         self.inventory,
    #     #         "filters",
    #     #         value,
    #     #     )
    #     #     self.inventory.filters = result
    #     # else:
    #     #     self.inventory.filters = value

    # =========================================================================

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[uint16]), ensure_bar_less_than_inventory_size
        ),
    )
    """
    The limiting bar of the inventory. Used to prevent a the final-most
    slots in the inventory from accepting items.

    Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    exceeds the Entity's ``inventory_size`` attribute.

    :getter: Gets the bar location of the inventory, or ``None`` if not set.
    :setter: Sets the bar location of the inventory. Removes the entry from
        the ``inventory`` object.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    :exception IndexError: If the set value lies outside of the range
        ``[0, 65536)``.
    """

    # @property
    # def bar(self) -> uint16:
    #     """
    #     The limiting bar of the inventory. Used to prevent a the final-most
    #     slots in the inventory from accepting items.

    #     Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    #     exceeds the Entity's ``inventory_size`` attribute.

    #     :getter: Gets the bar location of the inventory, or ``None`` if not set.
    #     :setter: Sets the bar location of the inventory. Removes the entry from
    #         the ``inventory`` object.

    #     :exception TypeError: If set to anything other than an ``int`` or
    #         ``None``.
    #     :exception IndexError: If the set value lies outside of the range
    #         ``[0, 65536)``.
    #     """
    #     return self.inventory.bar

    # @bar.setter
    # def bar(self, value: uint16):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InventoryFilters,
    #         self.inventory,
    #         "bar",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self, __class__.Format.InventoryFilters, self.inventory, "bar", value
    #     #     )
    #     #     self.inventory.bar = result
    #     # else:
    #     #     self.inventory.bar = value

    # =========================================================================

    def set_inventory_filter(
        self,
        index: int64,
        item: Optional[ItemName],
        quality: QualityName = "normal",
        comparator: Comparator = "=",
    ):
        """
        Sets the item filter at a particular index. If ``item`` is set to
        ``None``, the item filter at that location is removed.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception TypeError: If ``index`` is not an ``int`` or if ``item`` is
            neither a ``str`` nor ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception IndexError: If ``index`` lies outside the range
            ``[0, inventory_size)``.
        """
        if item is not None:
            new_entry = AttrsItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        # new_filters = (
        #     self.inventory.filters if self.inventory.filters is not None else []
        # )

        # Check to see if filters already contains an entry with the same index
        found_index = None
        for i, filter in enumerate(self.filters):
            if filter.index == index + 1:  # Index already exists in the list
                if item is None:
                    # Delete the entry
                    del self.filters[i]
                else:
                    # Modify the existing value inplace
                    self.filters[i].name = item
                    self.filters[i].quality = quality
                    self.filters[i].comparator = comparator
                found_index = i
                break

        if found_index is None:
            # If no entry with the same index was found
            self.filters.append(new_entry)

    # def set_inventory_filters(self, filters: list):
    #     """
    #     Sets all the inventory filters of the Entity.

    #     ``filters`` can be either of the following formats::

    #         [{"index": int, "signal": {"name": item_name_1, "type": "item"}}, ...]
    #         # Or
    #         [{"index": int, "signal": item_name_1}, ...]
    #         # Or
    #         [item_name_1, item_name_2, ...]

    #     With the second format, the index of each item is set to it's position
    #     in the list. ``filters`` can also be ``None``, which will wipe all
    #     inventory filters that the Entity has.

    #     :param filters: The inventory filters to give the Entity.

    #     :exception DataFormatError: If the ``filters`` argument does not match
    #         the specification above.
    #     :exception InvalidItemError: If the item name of one of the entries is
    #         not valid.
    #     :exception IndexError: If the index of one of the entries lies outside
    #         the range ``[0, inventory_size)``.
    #     """
    #     result = attempt_and_reissue(
    #         self, __class__.Format.InventoryFilters, self.inventory, "filters", filters
    #     )
    #     self.inventory.filters = result

    # =========================================================================

    def merge(self, other: "InventoryFilterMixin"):
        super().merge(other)

        self.filters = other.filters  # TODO: copy?
        self.bar = other.bar


draftsman_converters.add_schema(
    {"$id": "factorio:filtered_inventory_mixin"},
    InventoryFilterMixin,
    lambda fields: {
        ("inventory", "filters"): fields.filters.name,
        ("inventory", "bar"): fields.bar.name,
    },
)
