# transport_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitReadContentsMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import transport_belts
from draftsman.data import entities

import warnings


class TransportBelt(
    CircuitReadContentsMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that transports items.
    """

    def __init__(self, name=transport_belts[0], **kwargs):
        # type: (str, **dict) -> None
        super(TransportBelt, self).__init__(name, transport_belts, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {
                "object-layer",
                "item-layer",
                "transport-belt-layer",
                "water-tile",
            }

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
