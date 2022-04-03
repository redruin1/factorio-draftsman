# inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes import Entity
from draftsman.classes.mixins import (
    StackSizeMixin,
    CircuitReadHandMixin,
    ModeOfOperationMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import inserters

import warnings


class Inserter(
    StackSizeMixin,
    CircuitReadHandMixin,
    ModeOfOperationMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """ """

    def __init__(self, name=inserters[0], **kwargs):
        # type: (str, **dict) -> None
        super(Inserter, self).__init__(name, inserters, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
