# loader.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import FiltersMixin, IOTypeMixin, DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import loaders
from draftsman.data import entities

import warnings


class Loader(FiltersMixin, IOTypeMixin, DirectionalMixin, Entity):
    """
    An entity that inserts items directly from a belt to an inventory or
    vise-versa.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **DirectionalMixin._exports,
    #     **IOTypeMixin._exports,
    #     **FiltersMixin._exports,
    # }
    # fmt: on
    class Format(
        FiltersMixin.Format,
        IOTypeMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        pass

    def __init__(self, name=loaders[0], **kwargs):
        # type: (str, **dict) -> None
        super(Loader, self).__init__(name, loaders, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__
