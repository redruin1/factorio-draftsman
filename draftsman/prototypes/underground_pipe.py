# underground_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import underground_pipes

import warnings


class UndergroundPipe(DirectionalMixin, Entity):
    """
    A pipe that transports fluids underneath other entities.
    """

    def __init__(self, name=underground_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(UndergroundPipe, self).__init__(name, underground_pipes, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
