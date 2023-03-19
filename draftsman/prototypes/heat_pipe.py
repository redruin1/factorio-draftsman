# heat_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import heat_pipes
from draftsman.data import entities

import warnings


class HeatPipe(Entity):
    """
    An entity used to transfer thermal energy.
    """

    # fmt: off
    _exports = {
        **Entity._exports
    }
    # fmt: on

    def __init__(self, name=heat_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(HeatPipe, self).__init__(name, heat_pipes, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args
