# infinity_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.error import DataFormatError, InvalidItemError, InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import infinity_containers
from draftsman.data import items

from schema import SchemaError
import six
import warnings


class InfinityContainer(RequestItemsMixin, Entity):
    """
    An entity used to create an infinite amount of any item.
    """

    def __init__(self, name=infinity_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(InfinityContainer, self).__init__(name, infinity_containers, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.infinity_settings = kwargs["infinity_settings"]
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def infinity_settings(self):
        # type: () -> dict
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
        return self._infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value):
        # type: (dict) -> None
        try:
            value = signatures.INFINITY_CONTAINER.validate(value)
            self._infinity_settings = value
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def remove_unfiltered_items(self):
        # type: () -> bool
        """
        Whether or not to remove items that exceed the amounts specified in the
        ``InfinityContainer``'s filters.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.infinity_settings.get("remove_unfiltered_items", None)

    @remove_unfiltered_items.setter
    def remove_unfiltered_items(self, value):
        # type: (bool) -> None
        if value is None:
            self.infinity_settings.pop("remove_unfiltered_items", None)
        elif isinstance(value, bool):
            self.infinity_settings["remove_unfiltered_items"] = value
        else:
            raise TypeError("'remove_unfiltered_items' must be a bool or None")

    # =========================================================================

    def set_infinity_filter(self, index, item, mode="at-least", count=None):
        # type: (int, str, str, int) -> None
        """
        Sets an infinity filter.

        :param index: The index of the filter to set.
        :param name: The name of the item to interact with.
        :param mode: The manner in which to set the filter. Can be one of
            ``"at-least"``, ``"at-most"``, or ``"exactly"``.
        :param count: The amount of the item to request. If set to ``None``, the
            amount set will default to the stack size of ``name``.

        :exception TypeError: If ``index`` is not an ``int``, if ``name`` is not
            a ``str``, if ``mode`` is not a ``str``, or if ``count`` is not an
            ``int``.
        :exception IndexError: If ``index`` is outside the range ``[0, 1000)``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception InvalidModeError: If ``mode`` is not one of the three values
            specified above.
        """
        try:
            index = signatures.INTEGER.validate(index)
            item = signatures.STRING_OR_NONE.validate(item)
            mode = signatures.STRING.validate(mode)
            count = signatures.INTEGER_OR_NONE.validate(count)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if not 0 <= index < 1000:
            raise IndexError("Filter index {} not in range [0, 1000)")
        if item is not None and item not in items.raw:
            raise InvalidItemError(item)
        if mode not in {"at-least", "at-most", "exactly"}:
            raise InvalidModeError(mode)
        if count is None:  # default count to the item's stack size
            count = 0 if item is None else items.raw[item]["stack_size"]
        if count < 0:
            raise ValueError(
                "Infinity filter count ({}) must be positive".format(count)
            )

        if "filters" not in self.infinity_settings:
            self.infinity_settings["filters"] = []

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.infinity_settings["filters"]):
            if index + 1 == filter["index"]:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.infinity_settings["filters"][i]
                else:  # Set the new value
                    self.infinity_settings["filters"][i] = {
                        "index": index + 1,
                        "name": item,
                        "count": count,
                        "mode": mode,
                    }
                return

        # If no entry with the same index was found
        self.infinity_settings["filters"].append(
            {"name": item, "count": count, "mode": mode, "index": index + 1}
        )

    def set_infinity_filters(self, filters):
        # type: (list) -> None
        """
        Sets all of the infinity filters for the ``InfinityContainer``. Removes
        the filters if set to ``None``.

        :param filters: The filters to set, specified as :py:data:`.INFINITY_FILTERS`.

        :exception DataFormatError: If set to anything that does not match the
            :py:data:`.INFINITY_FILTERS` format.
        """
        if filters is None:
            self.infinity_settings.pop("filters", None)
        else:
            try:
                filters = signatures.INFINITY_FILTERS.validate(filters)
                self.infinity_settings["filters"] = filters
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)

    # def set_item_request(self, item, count):
    #     # type: (str, int) -> None
    #     self._handle_inventory_contents(item, count)

    #     super(InfinityContainer, self).set_item_request(item, count)
