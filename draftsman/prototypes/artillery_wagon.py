# artillery_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import artillery_wagons
from draftsman.data import entities

import warnings


class ArtilleryWagon(OrientationMixin, Entity):
    """
    An artillery train car.
    """

    # fmt: off
    _exports = {
        **Entity._exports,
        **OrientationMixin._exports
    }
    # fmt: on

    def __init__(self, name=artillery_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        """
        TODO
        """

        super(ArtilleryWagon, self).__init__(name, artillery_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args
