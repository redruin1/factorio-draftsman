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

        # Get the total number of module slots
        try:
            self._total_module_slots = entities.raw[self.name]["module_specification"][
                "module_slots"
            ]
        except KeyError:
            self._total_module_slots = 0

        # Keep track of the current module slots currently used
        self._module_slots_occupied = 0

        self.items = {}
        if "items" in kwargs:
            self.set_item_requests(kwargs["items"])
            self.unused_args.pop("items")
        self._add_export("items", lambda x: len(x) != 0)

    # =========================================================================

    @property
    def total_module_slots(self):
        # type: () -> int
        """
        The total number of module slots in the Entity. Not exported; read only.

        :type: ``int``
        """
        return self._total_module_slots

    # =========================================================================

    @property
    def module_slots_occupied(self):
        # type: () -> int
        """
        The total number of module slots that are currently taken by inserted
        modules. Not exported; read only.

        :type: ``int``
        """
        return self._module_slots_occupied

    # =========================================================================

    def set_item_request(self, item, count):
        # type: (str, int) -> None
        """
        Requests an amount of an item. Removes the item request if ``count`` is
        set to ``0`` or ``None``. Manages ``module_slots_occupied``.

        Raises :py:class:`~.ModuleCapacityWarning` if the total number of module
        slots taken exceeds the maximum number of module slots in this machine.

        :param item: The string name of the requested item.
        :param count: The desired amount of that item.

        :exception TypeError: If ``item`` is anything other than a ``str``, or
            if ``count`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        """
        # TODO: what if negative amount?
        try:
            item = signatures.STRING.validate(item)
            count = signatures.INTEGER_OR_NONE.validate(count)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        # if item not in items.raw:
        #     raise InvalidItemError("'{}'".format(item))

        # Only increment module slots if the item is a module
        if item in modules.raw:
            if count is None or 0:
                self._module_slots_occupied -= self.items.pop(item, None)
                return
            else:
                self._module_slots_occupied += count

        self.items[item] = count

        # Make sure we dont have too many modules in the Entity
        if self.module_slots_occupied > self.total_module_slots:
            warnings.warn(
                "Current number of module slots used ({}) greater than max "
                "module capacity ({})".format(
                    self.module_slots_occupied, self.total_module_slots
                ),
                ModuleCapacityWarning,
                stacklevel=2,
            )

    def set_item_requests(self, items):
        # type: (dict) -> None
        """
        Sets all of the item requests for the Entity. Takes ``items`` in the
        format::

            {item_1: count_1, item_2: count_2, ...}

        where ``item_x`` is a ``str`` and ``count_x`` is a positive integer.

        Raises :py:class:`~.ModuleCapacityWarning` if the total number of module
        slots taken exceeds the maximum number of module slots in this machine.

        :param items: A dictionary of the desired items in the format specified
            above.

        :exception TypeError: If ``item_x`` is anything other than a ``str``, or
            if ``count_x`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item_x`` is not a valid item name.
        """
        # TODO: fix this to pre check for errors and do hard set instead of
        # calling set_item_request
        if items is None:
            self.items = {}
            self._module_slots_occupied = 0
        else:
            for name, count in items.items():
                self.set_item_request(name, count)
