# splitter.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data import items

from draftsman.data.entities import splitters


class Splitter(DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = splitters[0], **kwargs):
        if name not in splitters:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Splitter, self).__init__(name, **kwargs)

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
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_filter(self, item: str) -> None:
        """
        Sets the Splitter's filter to `item`. Default output side is left.
        """
        if item in items.all or item is None:
            self.filter = item
        else:
            raise ValueError("'{}' is not a valid item name".format(item))

    def set_input_priority(self, side: str) -> None:
        """
        Sets the Splitter's input priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.input_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))

    def set_output_priority(self, side: str) -> None:
        """
        Sets the Splitter's output priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.output_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))