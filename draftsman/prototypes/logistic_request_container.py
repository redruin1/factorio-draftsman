# logistic_request_container.py

from draftsman.prototypes.mixins import (
    ModeOfOperationMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    RequestFiltersMixin, InventoryMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import logistic_request_containers


class LogisticRequestContainer(ModeOfOperationMixin, ControlBehaviorMixin, 
                               CircuitConnectableMixin, RequestFiltersMixin, 
                               InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_request_containers[0], **kwargs):
        if name not in logistic_request_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LogisticRequestContainer, self).__init__(name, **kwargs)

        self.request_from_buffers = None
        if "request_from_buffers" in kwargs:
            self.set_request_from_buffers(kwargs["request_from_buffers"])
            self.unused_args.pop("request_from_buffers")
        self._add_export("request_from_buffers", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_request_from_buffers(self, value: bool) -> None:
        """
        Sets whether or not this requester can recieve items from buffer chests.
        """
        self.request_from_buffers = signatures.BOOLEAN.validate(value)