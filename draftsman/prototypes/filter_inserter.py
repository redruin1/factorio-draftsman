# filter_inserter.py

from draftsman.prototypes.mixins import (
    FiltersMixin, StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin,
    CircuitConditionMixin, EnableDisableMixin, LogisticConditionMixin,
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import filter_inserters


class FilterInserter(FiltersMixin, StackSizeMixin, CircuitReadHandMixin, 
                     ModeOfOperationMixin, CircuitConditionMixin, 
                     EnableDisableMixin, LogisticConditionMixin, 
                     ControlBehaviorMixin, CircuitConnectableMixin, 
                     DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = filter_inserters[0], **kwargs):
        if name not in filter_inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(FilterInserter, self).__init__(name, **kwargs)

        self.filter_mode = None
        if "filter_mode" in kwargs:
            self.set_filter_mode(kwargs["filter_mode"])
        self._add_export("filter_mode", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_filter_mode(self, mode: str) -> None:
        """
        Sets the filter mode. Can be either 'whitelist' or 'blacklist'.
        """
        if mode in {"whitelist", "blacklist", None}:
            self.filter_mode = mode
        else:
            raise ValueError("'{}' is not a valid filter mode".format(mode))