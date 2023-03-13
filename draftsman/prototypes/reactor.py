# reactor.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import reactors

import warnings


class Reactor(RequestItemsMixin, Entity):
    """
    An entity that converts a fuel into thermal energy.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **RequestItemsMixin._exports
    # }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(RequestItemsMixin._exports)

    def __init__(self, name=reactors[0], **kwargs):
        # type: (str, **dict) -> None
        super(Reactor, self).__init__(name, reactors, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
