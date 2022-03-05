# electric_pole.py

from draftsman.prototypes.mixins import (
    CircuitConnectableMixin, PowerConnectableMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import electric_poles


class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str = electric_poles[0], **kwargs):
        if name not in electric_poles:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(ElectricPole, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))