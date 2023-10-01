# container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    CircuitConnectableMixin,
    InventoryMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import containers, raw

import warnings


class Container(InventoryMixin, RequestItemsMixin, CircuitConnectableMixin, Entity):
    """
    An entity that holds items.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **CircuitConnectableMixin._exports,
    #     **RequestItemsMixin._exports,
    #     **InventoryMixin._exports,
    # }
    # fmt: on
    class Format(
        InventoryMixin.Format,
        RequestItemsMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        pass

    def __init__(self, name=containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(Container, self).__init__(name, containers, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__
