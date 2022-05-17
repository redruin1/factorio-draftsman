# beacon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, RequestItemsMixin
from draftsman.error import InvalidItemError
from draftsman import utils
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

from draftsman.data.entities import beacons
from draftsman.data import modules
from draftsman.data import items

import warnings


class Beacon(ModulesMixin, RequestItemsMixin, Entity):
    """
    An entity designed to apply module effects to other machine's in it's radius.
    """

    def __init__(self, name=beacons[0], **kwargs):
        # type: (str, **dict) -> None
        super(Beacon, self).__init__(name, beacons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    @utils.reissue_warnings
    def set_item_request(self, item, count):
        # type: (str, int) -> None
        # Make sure the item exists
        # if item not in items.raw:
        #     raise InvalidItemError("'{}'".format(item))

        if item in items.raw and item not in modules.raw:
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

        super(Beacon, self).set_item_request(item, count)
