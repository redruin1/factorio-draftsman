# storage_tank.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import storage_tanks

import warnings


class StorageTank(CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    An entity that stores a fluid.
    """

    def __init__(self, name=storage_tanks[0], **kwargs):
        # type: (str, **dict) -> None
        super(StorageTank, self).__init__(name, storage_tanks, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
