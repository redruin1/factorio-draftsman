# container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, InventoryMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import containers, raw

import warnings


class Container(CircuitConnectableMixin, InventoryMixin, Entity):
    """
    * `wooden-chest`
    * `iron-chest`
    * `steel-chest`
    * `logistic-chest-active-provider`
    * `logistic-chest-passive-provider`
    """

    def __init__(self, name=containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(Container, self).__init__(name, containers, **kwargs)

        self._inventory_bar_enabled = raw[self.name].get("enable_inventory_bar", True)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
