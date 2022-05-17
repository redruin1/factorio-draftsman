# request_items.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities, modules, items
from draftsman.error import InvalidItemError
from draftsman.warning import ModuleCapacityWarning

from schema import SchemaError
import six
import warnings


class RequestItemsMixin(object):
    """
    Enables an entity to request items during its construction. Note that this
    is *not* for Logistics requests such as requester and buffer chests (that's
    what :py:class:`~.mixins.request_filters.RequestFiltersMixin` is for).
    Instead this is for specifying additional construction components, things
    like speed modules for beacons or productivity modules for assembling
    machines.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(RequestItemsMixin, self).__init__(name, similar_entities, **kwargs)

        self.items = {}
        if "items" in kwargs:
            self.set_item_requests(kwargs["items"])
            self.unused_args.pop("items")
        self._add_export("items", lambda x: len(x) != 0)

    # =========================================================================

    def set_item_request(self, item, count):
        # type: (str, int) -> None
        """
        Requests an amount of an item. Removes the item request if ``count`` is
        set to ``0`` or ``None``. Manages ``module_slots_occupied``.

        Raises a number of warnings if the requested item is mismatched for the
        type of entity you're requesting items for. For example,
        :py:class:`.ModuleLimitationWarning` will be raised when requesting an
        item that is not a module to a Beacon entity.

        :param item: The string name of the requested item.
        :param count: The desired amount of that item.

        :exception TypeError: If ``item`` is anything other than a ``str``, or
            if ``count`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception ValueError: If ``count`` is less than zero.
        """
        try:
            item = signatures.STRING.validate(item)
            count = signatures.INTEGER_OR_NONE.validate(count)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if item not in items.raw:
            raise InvalidItemError("'{}'".format(item))
        if count is not None and count < 0:
            raise ValueError("'count' must be a positive number")

        if count is None or count == 0:
            self.items.pop(item, None)
        else:
            self.items[item] = count

    def set_item_requests(self, items):
        # type: (dict) -> None
        """
        Sets all of the item requests for the Entity. Takes ``items`` as a
        ``dict`` in the format::

            {item_1: count_1, item_2: count_2, ...}

        where ``item_x`` is a ``str`` and ``count_x`` is a positive integer.

        :param items: A dictionary of the desired items in the format specified
            above.

        :exception TypeError: If ``item_x`` is anything other than a ``str``, or
            if ``count_x`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item_x`` is not a valid item name.
        :exception ValueError: If ``count_x`` is less than zero.
        """
        if items is None:
            self.items = {}
            # TODO: fix this as well, this sucks
            if hasattr(self, "module_slots_occupied"):
                self._module_slots_occupied = 0
            if hasattr(self, "inventory_slots_occupied"):
                self._inventory_slots_occupied = 0
        else:
            self.items = {}
            for name, count in items.items():
                self.set_item_request(name, count)
