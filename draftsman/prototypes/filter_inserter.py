# filter_inserter.py

from draftsman.prototypes.mixins import (
    FiltersMixin, StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin,
    CircuitConditionMixin, EnableDisableMixin, LogisticConditionMixin,
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import filter_inserters

import warnings


class FilterInserter(FiltersMixin, StackSizeMixin, CircuitReadHandMixin, 
                     ModeOfOperationMixin, CircuitConditionMixin, 
                     EnableDisableMixin, LogisticConditionMixin, 
                     ControlBehaviorMixin, CircuitConnectableMixin, 
                     DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = filter_inserters[0], **kwargs):
        # type: (str, **dict) -> None
        super(FilterInserter, self).__init__(name, filter_inserters, **kwargs)

        self.filter_mode = None
        if "filter_mode" in kwargs:
            self.set_filter_mode(kwargs["filter_mode"])
        self._add_export("filter_mode", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_filter_mode(self, mode):
        # type: (str) -> None
        """
        Sets the filter mode. Can be either 'whitelist' or 'blacklist'.
        """
        if mode in {"whitelist", "blacklist", None}:
            self.filter_mode = mode
        else:
            raise ValueError("'{}' is not a valid filter mode".format(mode))