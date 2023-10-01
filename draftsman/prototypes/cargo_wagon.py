# cargo_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    InventoryFilterMixin,
    OrientationMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import cargo_wagons
from draftsman.data import entities

import warnings


class CargoWagon(RequestItemsMixin, InventoryFilterMixin, OrientationMixin, Entity):
    """
    A train wagon that holds items as cargo.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **OrientationMixin._exports,
    #     **InventoryFilterMixin._exports,
    #     **RequestItemsMixin._exports,
    # }
    # fmt: on
    class Format(
        RequestItemsMixin.Format,
        InventoryFilterMixin.Format,
        OrientationMixin.Format,
        Entity.Format,
    ):
        pass

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

    # TODO: check for item requests exceeding cargo capacity

    # =========================================================================

    __hash__ = Entity.__hash__
