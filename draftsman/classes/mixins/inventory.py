# inventory.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import DraftsmanError
from draftsman.warning import IndexWarning

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
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Not exported; read
        only.

        :type: ``int``
        """
        return self._inventory_size

    # =========================================================================

    @property
    def inventory_bar_enabled(self):
        # type: () -> bool
        """
        Whether or not this Entity has its inventory limiting bar enabled.
        Equivalent to the ``"enable_inventory_bar"`` key in Factorio's
        ``data.raw``. Not exported; read only.

        :type: ``bool``
        """
        return self._inventory_bar_enabled

    # =========================================================================

    @property
    def bar(self):
        # type: () -> int
        """
        The limiting bar of the inventory. Used to prevent a the final-most
        slots in the inventory from accepting items.

        Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
        exceeds the Entity's ``inventory_size`` attribute.

        :getter: Gets the bar location of the inventory.
        :setter: Sets the bar location of the inventory.
        :type: ``int``

        :exception DraftsmanError: If attempting to set the bar of an Entity
            that has the ``inventory_bar_enabled`` attribute set to ``False``.
        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        :exception IndexError: If the set value lies outside of the range
            ``[0, 65536)``.
        """
        return self._bar

    @bar.setter
    def bar(self, value):
        # type: (int) -> None
        if not self.inventory_bar_enabled:
            raise DraftsmanError("This entity does not have bar control")

        if value is None:
            self._bar = None
        elif isinstance(value, int):
            if not 0 <= value < 65536:
                # Error if out of range
                raise IndexError("Bar index ({}) not in range [0, 65536)".format(value))
            elif value >= self.inventory_size:
                # Warn if greater than what makes sense
                warnings.warn(
                    "Bar index ({}) not in range [0, {})".format(
                        value, self.inventory_size
                    ),
                    IndexWarning,
                    stacklevel=2,
                )
            self._bar = value
        else:
            raise TypeError("'bar' must be an int or None")
