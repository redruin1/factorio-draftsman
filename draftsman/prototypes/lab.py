# lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import labs

import warnings


class Lab(RequestItemsMixin, Entity):
    """
    An entity that consumes items and produces research.
    """

    def __init__(self, name=labs[0], **kwargs):
        # type: (str, **dict) -> None
        super(Lab, self).__init__(name, labs, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
