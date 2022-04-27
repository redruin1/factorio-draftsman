# inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.constants import InserterModeOfOperation
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import inserters

import warnings


class Inserter(
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    Inserter Entity prototype.

    .. NOTE::

        In Factorio, the ``Inserter`` prototype includes both regular and filter
        inserters. In Draftsman, inserters are split into two different classes,
        :py:class:`~.Inserter` and :py:class:`~.FilterInserter`

    .. seealso::

        :py:class:`~.FilterInserter`
    """

    def __init__(self, name=inserters[0], **kwargs):
        # type: (str, **dict) -> None
        """
        TODO
        """
        super(Inserter, self).__init__(name, inserters, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
