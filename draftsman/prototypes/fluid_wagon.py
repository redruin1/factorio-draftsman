# fluid_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import fluid_wagons
from draftsman.data import entities

import warnings


class FluidWagon(OrientationMixin, Entity):
    """
    A train wagon that holds a fluid as cargo.
    """

    # fmt: off
    _exports = {
        **Entity._exports,
        **OrientationMixin._exports
    }
    # fmt: on

    def __init__(self, name=fluid_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(FluidWagon, self).__init__(name, fluid_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args
