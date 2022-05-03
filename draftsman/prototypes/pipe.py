# pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import pipes

import warnings


class Pipe(Entity):
    """
    An entity that transports a fluid.
    """

    def __init__(self, name=pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(Pipe, self).__init__(name, pipes, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
