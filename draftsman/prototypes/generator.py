# generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import generators

import warnings


class Generator(DirectionalMixin, Entity):
    """
    An entity that converts a fluid (usually steam) to electricity.
    """

    def __init__(self, name=generators[0], **kwargs):
        # type: (str, **dict) -> None
        super(Generator, self).__init__(name, generators, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
