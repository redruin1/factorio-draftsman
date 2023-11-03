# inventory_filter.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.data import entities
from draftsman.data import items
from draftsman.error import (
    InvalidItemError,
    DataFormatError,
)
from draftsman.signatures import InventoryFilters, Filters, uint16
from draftsman.warning import IndexWarning

from pydantic import BaseModel, Field, ValidationError, validate_call
import six
import warnings
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class InventoryFilterMixin:
    """
    Allows an Entity to set inventory filters. Only used on :py:class:`.CargoWagon`.
    """

    class Format(BaseModel):
        inventory: Optional[InventoryFilters] = Field(
            InventoryFilters(),
            description="""
            Custom inventory object just for cargo wagons. Note that this 
            contains the 'bar' key for this entity type specifically, which 
            differs from all other containers.
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.inventory = kwargs.get("inventory", InventoryFilters())

    # =========================================================================

    @property
    def inventory_size(self):
        # type: () -> int
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman. Not exported; read
        only.

        :type: ``int``
        """
        return entities.raw.get(self.name, {"inventory_size": None})["inventory_size"]

    # =========================================================================

    @property
    def inventory(self) -> InventoryFilters:
        """
        Inventory filter object. Contains the filter information under the
        ``"filters"`` key and the inventory limiting bar under the ``"bar"`` key.

        This attribute is in the following format::

            {
                "bar": int,
                "filters": [
                    {"index": int, "signal": {"name": str, "type": str}},
                    ...
                ]
            }

        :getter: Gets the value of the Entity's ``inventory`` object.
        :setter: Sets the value of the Entity's ``inventory`` object. Defaults
            to an empty ``dict`` if set to ``None``.
        :type: See :py:class:`draftsman.signatures.INVENTORY_FILTER`.

        :exception DataFormatError: If the set value differs from the
            ``INVENTORY_FILTER`` specification.
        """
        return self._root.inventory

    @inventory.setter
    def inventory(self, value: InventoryFilters):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self, type(self).Format, self._root, "inventory", value
            )

        if value is None:
            self._root.inventory = InventoryFilters()
        else:
            self._root.inventory = value

    # =========================================================================

    @property
    def filter_count(self) -> int:
        """
        The number of filter slots that this entity has. In this case, is
        equivalent to the number of inventory slots of the CargoWagon. Returns
        ``None`` if this entity's name is not recognized by Draftsman. Not
        exported; read only.
        """
        return self.inventory_size

    # =========================================================================

    @property
    def filters(self) -> Filters:
        """
        TODO
        """
        return self.inventory.filters

    @filters.setter
    def filters(self, value: Filters):
        if self.validate_assignment:
            attempt_and_reissue(self, "filters", value)

        self.inventory.filters = value

    # =========================================================================

    @property
    def bar(self) -> uint16:
        """
        The limiting bar of the inventory. Used to prevent a the final-most
        slots in the inventory from accepting items.

        Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
        exceeds the Entity's ``inventory_size`` attribute.

        :getter: Gets the bar location of the inventory, or ``None`` if not set.
        :setter: Sets the bar location of the inventory. Removes the entry from
            the ``inventory`` object.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        :exception IndexError: If the set value lies outside of the range
            ``[0, 65536)``.
        """
        return self.inventory.bar

    @bar.setter
    def bar(self, value: uint16):
        if self.validate_assignment:
            attempt_and_reissue(self, "filters", value)

        self.inventory.filters = value

    # =========================================================================

    @validate_call
    def set_inventory_filter(self, index: int, item: str):
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

        if self.inventory.filters is None:
            self.inventory.filters = Filters()

        # TODO: maybe make an 'ItemID' item with a custom validator?
        if item is not None:
            if item not in items.raw:
                # TODO: this should be a warning, in case its just that the item
                # is unknown by Draftsman
                raise InvalidItemError(item)

        if not 0 <= index < self.inventory_size:
            raise IndexError(
                "Filter index ({}) not in range [0, {})".format(
                    index, self.inventory_size
                )
            )

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.inventory.filters.root): # TODO: change this
            if filter["index"] == index + 1:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.inventory.filters.root[i]
                else:  # Set the new value
                    # self.inventory["filters"][i] = {"index": index+1,"name": item}
                    self.inventory.filters.root[i].name = item
                return

        # If no entry with the same index was found
        self.inventory.filters.root.append({"index": index + 1, "name": item})

    def set_inventory_filters(self, filters):
        # type: (list) -> None
        """
        Sets all the inventory filters of the Entity.

        ``filters`` can be either of the following formats::

            [{"index": int, "signal": {"name": item_name_1, "type": "item"}}, ...]
            # Or
            [{"index": int, "signal": item_name_1}, ...]
            # Or
            [item_name_1, item_name_2, ...]

        With the second format, the index of each item is set to it's position
        in the list. ``filters`` can also be ``None``, which will wipe all
        inventory filters that the Entity has.

        :param filters: The inventory filters to give the Entity.

        :exception DataFormatError: If the ``filters`` argument does not match
            the specification above.
        :exception InvalidItemError: If the item name of one of the entries is
            not valid.
        :exception IndexError: If the index of one of the entries lies outside
            the range ``[0, inventory_size)``.
        """
        if filters is None:
            self.inventory.pop("filters", None)
            return

        try:
            filters = Filters(root=filters).model_dump(
                by_alias=True,
                exclude_none=True,
                exclude_defaults=True,
            )
        except ValidationError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are item signals
        for item in filters:
            if item["name"] not in items.raw:
                raise InvalidItemError(item)

        for i in range(len(filters)):
            self.set_inventory_filter(filters[i]["index"] - 1, filters[i]["name"])

    # =========================================================================

    def merge(self, other):
        # type: (Entity) -> None
        super().merge(other)

        # self.inventory = {}
        # self.bar = other.bar
        # self.set_inventory_filters(other.inventory.get("filters", None))
        self.inventory = other.inventory

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.inventory == other.inventory
