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
from typing import ClassVar
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
    class Format(
        CircuitReadContentsMixin.Format,
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        EnableDisableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format
    ):
        class ControlBehavior(
            CircuitReadContentsMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            EnableDisableMixin.ControlFormat,
        ):
            pass
        
        control_behavior: ControlBehavior | None = ControlBehavior()

    def __init__(self, name=transport_belts[0], **kwargs):
        # type: (str, **dict) -> None
        super(TransportBelt, self).__init__(name, transport_belts, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__
