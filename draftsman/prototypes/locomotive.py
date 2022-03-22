# locomotive.py

from draftsman.classes import Entity
from draftsman.classes.mixins import ColorMixin, OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import locomotives

import warnings


class Locomotive(ColorMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name = locomotives[0], **kwargs):
        # type: (str, **dict) -> None
        super(Locomotive, self).__init__(name, locomotives, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )