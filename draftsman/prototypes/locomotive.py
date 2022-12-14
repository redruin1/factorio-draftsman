# locomotive.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ColorMixin, OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import locomotives
from draftsman.data import entities

import warnings


class Locomotive(ColorMixin, OrientationMixin, Entity):
    """
    A train car that moves other wagons around using a fuel.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **OrientationMixin._exports,
    #     **ColorMixin._exports
    # }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(OrientationMixin._exports)
    _exports.update(ColorMixin._exports)

    def __init__(self, name=locomotives[0], **kwargs):
        # type: (str, **dict) -> None
        super(Locomotive, self).__init__(name, locomotives, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
