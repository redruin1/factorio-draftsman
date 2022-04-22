# turret.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import turrets

import warnings


class Turret(DirectionalMixin, Entity):
    def __init__(self, name=turrets[0], **kwargs):
        # type: (str, **dict) -> None
        super(Turret, self).__init__(name, turrets, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
