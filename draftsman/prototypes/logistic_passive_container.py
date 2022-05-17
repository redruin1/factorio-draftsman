# logistic_passive_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    CircuitConnectableMixin,
    InventoryMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import logistic_passive_containers

import warnings


class LogisticPassiveContainer(
    InventoryMixin, RequestItemsMixin, CircuitConnectableMixin, Entity
):
    """
    A logistics container that provides it's contents to the logistic network
    when needed by the network.
    """

    def __init__(self, name=logistic_passive_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(LogisticPassiveContainer, self).__init__(
            name, logistic_passive_containers, **kwargs
        )

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
