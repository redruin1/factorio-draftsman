# mining_drill.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman import utils
from draftsman.warning import DraftsmanWarning, ItemLimitationWarning

from draftsman.data.entities import mining_drills
from draftsman.data import modules
from draftsman.data import items

import warnings


class MiningDrill(
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that extracts resources from the environment.
    """

    def __init__(self, name=mining_drills[0], **kwargs):
        # type: (str, **dict) -> None
        super(MiningDrill, self).__init__(name, mining_drills, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    @utils.reissue_warnings
    def set_item_request(self, item, amount):
        # type: (str, int) -> None
        # Make sure the item exists
        # if item not in items.raw:
        #     raise InvalidItemError(item)

        if item in items.raw and item not in modules.raw:
            warnings.warn(
                "Item '{}' cannot be placed in MiningDrill".format(item),
                ItemLimitationWarning,
                stacklevel=2,
            )

        # self._handle_module_slots(item, amount)

        super(MiningDrill, self).set_item_request(item, amount)
