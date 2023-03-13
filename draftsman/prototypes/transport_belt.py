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
from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import transport_belts
from draftsman.data import entities

from schema import SchemaError
import six
import warnings


class TransportBelt(
    CircuitReadContentsMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that transports items.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **DirectionalMixin._exports,
    #     **CircuitConnectableMixin._exports,
    #     **ControlBehaviorMixin._exports,
    #     **EnableDisableMixin._exports,
    #     **LogisticConditionMixin._exports,
    #     **CircuitConditionMixin._exports,
    #     **CircuitReadContentsMixin._exports,
    # }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(DirectionalMixin._exports)
    _exports.update(CircuitConnectableMixin._exports)
    _exports.update(ControlBehaviorMixin._exports)
    _exports.update(EnableDisableMixin._exports)
    _exports.update(LogisticConditionMixin._exports)
    _exports.update(CircuitConditionMixin._exports)
    _exports.update(CircuitReadContentsMixin._exports)

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

    # =========================================================================

    @ControlBehaviorMixin.control_behavior.setter
    def control_behavior(self, value):
        # type: (dict) -> None
        try:
            self._control_behavior = (
                signatures.TRANSPORT_BELT_CONTROL_BEHAVIOR.validate(value)
            )
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
