# constant_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import constant_combinators

import warnings


class ConstantCombinator(
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
):
    """
    TODO: maybe keep signal filters internally as an array of Signal objects,
    and then use Signal.to_dict() during that stage?
    """

    def __init__(self, name=constant_combinators[0], **kwargs):
        # type: (str, **dict) -> None
        super(ConstantCombinator, self).__init__(name, constant_combinators, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    def set_signal(self, index, signal, count=0):
        # type: (int, str, int) -> None
        """ """
        # Check validity before modifying self
        index = signatures.INTEGER.validate(index)
        signal = signatures.SIGNAL_ID.validate(signal)
        count = signatures.INTEGER.validate(count)

        if "filters" not in self.control_behavior:
            self.control_behavior["filters"] = []

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.control_behavior["filters"]):
            if index + 1 == filter["index"]:  # Index already exists in the list
                if signal is None:  # Delete the entry
                    del self.control_behavior["filters"][i]
                else:  # Set the new value
                    self.control_behavior["filters"][i] = {
                        "index": index + 1,
                        "signal": signal,
                        "count": count,
                    }
                return

        # If no entry with the same index was found
        self.control_behavior["filters"].append(
            {"index": index + 1, "signal": signal, "count": count}
        )

    def get_signal(self, index):
        # type: (int) -> dict
        """ """
        filters = self.control_behavior.get("filters", None)
        if not filters:
            return None

        return next((item for item in filters if item["index"] == index + 1), None)

    def set_signals(self, signals):
        # type: (list) -> None
        """ """
        signals = signatures.SIGNAL_FILTERS.validate(signals)

        if signals is None:
            self.control_behavior.pop("filters", None)
        else:
            self.control_behavior["filters"] = signals
