# underground_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import IOTypeMixin, DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import underground_belts
from draftsman.data import entities

import warnings


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    A transport belt that transfers items underneath other entities.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **DirectionalMixin._exports,
    #     **IOTypeMixin._exports
    # }
    # fmt: on
    class Format(IOTypeMixin.Format, DirectionalMixin.Format, Entity.Format):
        pass

    def __init__(self, name=underground_belts[0], **kwargs):
        # type: (str, **dict) -> None
        super(UndergroundBelt, self).__init__(name, underground_belts, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__
