# logistic_request_container.py

from urllib import request
from draftsman.classes import Entity
from draftsman.classes.mixins import (
    ModeOfOperationMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    RequestFiltersMixin, InventoryMixin
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import logistic_request_containers

import warnings


class LogisticRequestContainer(ModeOfOperationMixin, ControlBehaviorMixin, 
                               CircuitConnectableMixin, RequestFiltersMixin, 
                               InventoryMixin, Entity):
    """
    """
    def __init__(self, name = logistic_request_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(LogisticRequestContainer, self).__init__(
            name, logistic_request_containers, **kwargs
        )

        self.request_from_buffers = None
        if "request_from_buffers" in kwargs:
            self.request_from_buffers = kwargs["request_from_buffers"]
            self.unused_args.pop("request_from_buffers")
        self._add_export("request_from_buffers", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    # =========================================================================

    @property
    def request_from_buffers(self):
        # type: () -> bool
        """
        TODO
        """
        return self._request_from_buffers

    @request_from_buffers.setter
    def request_from_buffers(self, value):
        # type: (bool) -> None
        if value is None or isinstance(value, bool):
            self._request_from_buffers = value
        else:
            raise TypeError("'request_from_buffers' must be a bool or None")

    # def set_request_from_buffers(self, value):
    #     # type: (bool) -> None
    #     """
    #     Sets whether or not this requester can recieve items from buffer chests.
    #     """
    #     self.request_from_buffers = signatures.BOOLEAN.validate(value)