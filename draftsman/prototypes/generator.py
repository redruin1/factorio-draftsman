# generator.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import generators

import warnings


class Generator(DirectionalMixin, Entity):
    def __init__(self, name = generators[0], **kwargs):
        # type: (str, **dict) -> None
        super(Generator, self).__init__(name, generators, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )