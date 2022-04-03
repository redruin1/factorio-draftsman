# request_items.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities, modules, signals
from draftsman.error import InvalidItemError
from draftsman.warning import ModuleCapacityWarning

import warnings


class RequestItemsMixin(object):
    """
    NOTE: this is for module requests and stuff like that, not logistics!

    Think an assembling machine that needs speed modules inside of it
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
        Read only
        TODO
        """
        return self._total_module_slots

    # =========================================================================

    @property
    def module_slots_occupied(self):
        # type: () -> int
        """
        Read only
        TODO
        """
        return self._module_slots_occupied

    # =========================================================================

    def set_item_request(self, item, amount):
        # type: (str, int) -> None
        """
        Base method for setting a single item request.
        TODO
        """
        if amount is None:
            self._module_slots_occupied -= self.items.pop(item, None)
            return

        amount = signatures.INTEGER.validate(amount)
        self.items[item] = amount

        # Only increment module slots if the item is a module
        if item in modules.raw:
            self._module_slots_occupied += amount

        # Make sure we dont have too many modules in the Entity
        if self.module_slots_occupied > self.total_module_slots:
            warnings.warn(
                "Current number of module slots used ({}) greater than max "
                "module capacity ({})".format(
                    self.module_slots_occupied, self.total_module_slots
                ),
                ModuleCapacityWarning,
                stacklevel=3,
            )

    def set_item_requests(self, items):
        # type: (dict) -> None
        """
        TODO
        """
        if items is None:
            self.items = {}
            self._module_slots_occupied = 0
        else:
            for name, amount in items.items():
                self.set_item_request(name, amount)
