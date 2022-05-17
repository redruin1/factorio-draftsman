# lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, RequestItemsMixin
from draftsman import utils
from draftsman.warning import DraftsmanWarning, ItemLimitationWarning

from draftsman.data.entities import labs, raw
from draftsman.data import items, modules

import warnings


class Lab(ModulesMixin, RequestItemsMixin, Entity):
    """
    An entity that consumes items and produces research.
    """

    def __init__(self, name=labs[0], **kwargs):
        # type: (str, **dict) -> None
        super(Lab, self).__init__(name, labs, **kwargs)

        # Keep track of science packs that this lab can use
        self._inputs = raw[self.name]["inputs"]

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def inputs(self):
        # type: () -> list[str]
        """
        The inputs that this Lab uses to research. Not exported; read only.

        :type: ``list[str]``
        """
        return self._inputs

    # =========================================================================

    @utils.reissue_warnings
    def set_item_request(self, item, count):
        # type: (str, int) -> None
        if item not in modules.raw and item not in self.inputs:
            warnings.warn(
                "Item '{}' cannot be placed in Lab".format(item),
                ItemLimitationWarning,
                stacklevel=2,
            )

        # TODO: check the lab's limitations to see if the module is allowed
        # ('allowed_effects')
        # This is all for regular labs, but not necessarily modded ones.

        # TODO: check the amount of the science pack passed in; if its greater
        # than 10(?) issue an ItemCapacityWarning

        super(Lab, self).set_item_request(item, count)
