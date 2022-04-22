# beacon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.error import InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

from draftsman.data.entities import beacons
from draftsman.data import modules
from draftsman.data import signals

import warnings


class Beacon(RequestItemsMixin, Entity):
    def __init__(self, name=beacons[0], **kwargs):
        # type: (str, **dict) -> None
        super(Beacon, self).__init__(name, beacons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    def set_item_request(self, item, amount):
        # type: (str, int) -> None
        """
        Overwritten
        """
        # Make sure the item exists
        if item not in signals.item:  # TODO: maybe items.all instead?
            raise InvalidItemError("'{}'".format(item))

        if item not in modules.raw:
            warnings.warn(
                "Item '{}' cannot be placed in Beacon".format(item),
                ItemLimitationWarning,
                stacklevel=2,
            )

        if item in modules.categories["productivity"]:
            warnings.warn(
                "Cannot use '{}' in Beacon".format(item),
                ModuleLimitationWarning,
                stacklevel=2,
            )

        super(Beacon, self).set_item_request(item, amount)
