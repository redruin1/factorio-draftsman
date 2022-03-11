# beacon.py

from draftsman.prototypes.mixins import RequestItemsMixin, Entity
from draftsman.warning import DraftsmanWarning, ModuleLimitationWarning

from draftsman.data.entities import beacons
import draftsman.data.modules as modules

import warnings


class Beacon(RequestItemsMixin, Entity):
    def __init__(self, name = beacons[0], **kwargs):
        # type: (str, **dict) -> None
        super(Beacon, self).__init__(name, beacons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_item_request(self, item, amount):
        # type: (str, int) -> None
        """
        Overwritten
        """
        if item in modules.categories["productivity"]:
            warnings.warn(
                "cannot use '{}' in Beacon".format(item),
                ModuleLimitationWarning,
                stacklevel = 2
            )

        super().set_item_request(item, amount)