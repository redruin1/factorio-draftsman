# filter_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes import Entity
from draftsman.classes.mixins import (
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    ModeOfOperationMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import filter_inserters

import six
import warnings


class FilterInserter(
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    ModeOfOperationMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    TODO
    """

    def __init__(self, name=filter_inserters[0], **kwargs):
        # type: (str, **dict) -> None
        super(FilterInserter, self).__init__(name, filter_inserters, **kwargs)

        self.filter_mode = None
        if "filter_mode" in kwargs:
            self.filter_mode = kwargs["filter_mode"]
            self.unused_args.pop("filter_mode")
        self._add_export("filter_mode", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def filter_mode(self):
        # type: () -> str
        """
        TODO
        """
        return self._filter_mode

    @filter_mode.setter
    def filter_mode(self, value):
        # type: (str) -> None
        if value is None:
            self._filter_mode = value
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_modes = {"whitelist", "blacklist"}
            if value not in valid_modes:
                raise ValueError("'filter_mode' must be one of {}".format(valid_modes))
            self._filter_mode = value
        else:
            raise TypeError("'filter_mode' must be a str or None")