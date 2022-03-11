# rocket_silo.py

from draftsman.prototypes.mixins import Entity
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rocket_silos

import warnings


class RocketSilo(Entity):
    def __init__(self, name = rocket_silos[0], **kwargs):
        # type: (str, **dict) -> None
        super(RocketSilo, self).__init__(name, rocket_silos, **kwargs)

        self.auto_launch = None
        if "auto_launch" in kwargs:
            self.set_auto_launch(kwargs["auto_launch"])
            self.unused_args.pop("auto_launch")
        self._add_export("auto_launch", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_auto_launch(self, value):
        # type: (bool) -> None
        """
        """
        self.auto_launch = signatures.BOOLEAN.validate(value)