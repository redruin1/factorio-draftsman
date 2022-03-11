# loader.py

from draftsman.prototypes.mixins import (
    FiltersMixin, IOTypeMixin, DirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import loaders

import warnings


class Loader(FiltersMixin, IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = loaders[0], **kwargs):
        # type: (str, **dict) -> None
        super(Loader, self).__init__(name, loaders, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )