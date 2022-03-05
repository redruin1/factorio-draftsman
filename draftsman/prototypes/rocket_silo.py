# rocket_silo.py

from draftsman.prototypes.mixins import Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import rocket_silos


class RocketSilo(Entity):
    def __init__(self, name: str = rocket_silos[0], **kwargs):
        if name not in rocket_silos:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(RocketSilo, self).__init__(name, **kwargs)

        self.auto_launch = None
        if "auto_launch" in kwargs:
            self.set_auto_launch(kwargs["auto_launch"])
            self.unused_args.pop("auto_launch")
        self._add_export("auto_launch", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_auto_launch(self, value: bool) -> None:
        """
        """
        self.auto_launch = signatures.BOOLEAN.validate(value)