# reactor.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import reactors

import warnings


class Reactor(Entity):
    def __init__(self, name=reactors[0], **kwargs):
        # type: (str, **dict) -> None
        super(Reactor, self).__init__(name, reactors, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
