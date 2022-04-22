# constant_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.error import DataFormatError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import constant_combinators
from draftsman.data import entities

from schema import SchemaError
import six
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

        self._item_slot_count = entities.raw[self.name]["item_slot_count"]

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def item_slot_count(self):
        # type: () -> int
        """
        Read only
        TODO
        """
        return self._item_slot_count

    # =========================================================================

    def set_signal(self, index, signal, count=0):
        # type: (int, str, int) -> None
        """ """
        # Check validity before modifying self
        if not isinstance(index, six.integer_types):
            raise TypeError("'index' must be an int")
        try:
            signal = signatures.SIGNAL_ID_OR_NONE.validate(signal)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
        if not isinstance(count, six.integer_types):
            raise TypeError("'count' must be an int")

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

        if signals is None:
            self.control_behavior.pop("filters", None)
        else:
            try:
                signals = signatures.SIGNAL_FILTERS.validate(signals)
                self.control_behavior["filters"] = signals
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)
