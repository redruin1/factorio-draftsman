# turret.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin, DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import turrets

import warnings


class Turret(RequestItemsMixin, DirectionalMixin, Entity):
    """
    An entity that automatically targets and attacks other forces in range.
    """

    def __init__(self, name=turrets[0], **kwargs):
        # type: (str, **dict) -> None
        super(Turret, self).__init__(name, turrets, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
