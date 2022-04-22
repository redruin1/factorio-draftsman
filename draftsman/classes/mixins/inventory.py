# inventory.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import BarIndexError
from draftsman.warning import BarIndexWarning

import warnings


class InventoryMixin(object):
    """
    Enables the entity to have inventory control.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(InventoryMixin, self).__init__(name, similar_entities, **kwargs)

        self._inventory_size = entities.raw[self.name]["inventory_size"]

        self._inventory_bar_enabled = True

        self.bar = None
        if "bar" in kwargs:
            self.bar = kwargs["bar"]
            self.unused_args.pop("bar")
        self._add_export("bar", lambda x: x is not None)

    # =========================================================================

    @property
    def inventory_size(self):
        # type: () -> int
        """
        Read Only
        TODO
        """
        return self._inventory_size

    # =========================================================================

    @property
    def inventory_bar_enabled(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._inventory_bar_enabled

    # =========================================================================

    @property
    def bar(self):
        # type: () -> int
        """
        TODO
        """
        return self._bar

    @bar.setter
    def bar(self, value):
        # type: (int) -> None
        if not self.inventory_bar_enabled:
            raise BarIndexError("This entity does not have bar control")

        if value is None:
            self._bar = None
        elif isinstance(value, int):
            if not 0 <= value < 65536:
                # Error if out of range
                raise BarIndexError(
                    "Bar index ({}) not in range [0, 65536)".format(value)
                )
            elif value >= self.inventory_size:
                # Warn if greater than what makes sense
                warnings.warn(
                    "Bar index ({}) not in range [0, {})".format(
                        value, self.inventory_size
                    ),
                    BarIndexWarning,
                    stacklevel=2,
                )
            self._bar = value
        else:
            raise TypeError("'bar' must be an int or None")
