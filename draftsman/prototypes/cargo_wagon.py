# cargo_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import InventoryFilterMixin, OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import cargo_wagons
from draftsman.data import entities

import warnings


class CargoWagon(InventoryFilterMixin, OrientationMixin, Entity):
    """
    A train wagon that holds items as cargo.
    """

    # fmt: off
    _exports = {
        **Entity._exports,
        **OrientationMixin._exports,
        **InventoryFilterMixin._exports,
    }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(OrientationMixin._exports)
    _exports.update(InventoryFilterMixin._exports)

    def __init__(self, name=cargo_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(CargoWagon, self).__init__(name, cargo_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args
