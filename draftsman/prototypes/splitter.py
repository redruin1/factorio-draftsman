# splitter.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data import items

from draftsman.data.entities import splitters

import warnings


class Splitter(DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = splitters[0], **kwargs):
        # type: (str, **dict) -> None
        super(Splitter, self).__init__(name, splitters, **kwargs)

        self.input_priority = None
        if "input_priority" in kwargs:
            self.set_input_priority(kwargs["input_priority"])
            self.unused_args.pop("input_priority")
        self._add_export("input_priority", lambda x: x is not None)

        self.output_priority = None
        if "output_priority" in kwargs:
            self.set_output_priority(kwargs["output_priority"])
            self.unused_args.pop("output_priority")
        self._add_export("output_priority", lambda x: x is not None)

        self.filter = None
        if "filter" in kwargs:
            self.set_filter(kwargs["filter"])
            self.unused_args.pop("filter")
        self._add_export("filter", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_filter(self, item):
        # type: (str) -> None
        """
        Sets the Splitter's filter to `item`. Default output side is left.
        """
        if item in items.raw or item is None:
            self.filter = item
        else:
            raise ValueError("'{}' is not a valid item name".format(item))

    def set_input_priority(self, side):
        # type: (str) -> None
        """
        Sets the Splitter's input priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.input_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))

    def set_output_priority(self, side):
        # type: (str) -> None
        """
        Sets the Splitter's output priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.output_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))