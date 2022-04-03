# splitter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.error import InvalidItemError, InvalidSideError
from draftsman.warning import DraftsmanWarning

from draftsman.data import items

from draftsman.data.entities import splitters
from draftsman.data import entities

import six
from typing import Literal
import warnings


class Splitter(DirectionalMixin, Entity):
    """ """

    def __init__(self, name=splitters[0], **kwargs):
        # type: (str, **dict) -> None
        super(Splitter, self).__init__(name, splitters, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = entities.raw[self.name]["collision_mask"]
        else:  # pragma: no coverage
            self._collision_mask = {
                "object-layer",
                "item-layer",
                "transport-belt-layer",
                "water-tile",
            }

        self.input_priority = None
        if "input_priority" in kwargs:
            self.input_priority = kwargs["input_priority"]
            self.unused_args.pop("input_priority")
        self._add_export("input_priority", lambda x: x is not None)

        self.output_priority = None
        if "output_priority" in kwargs:
            self.output_priority = kwargs["output_priority"]
            self.unused_args.pop("output_priority")
        self._add_export("output_priority", lambda x: x is not None)

        self.filter = None
        if "filter" in kwargs:
            self.filter = kwargs["filter"]
            self.unused_args.pop("filter")
        self._add_export("filter", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def input_priority(self):
        # type: () -> Literal["left", "right", None]
        """
        TODO
        """
        return self._input_priority

    @input_priority.setter
    def input_priority(self, value):
        # type: (Literal["left", "right", None]) -> None
        if value is None:
            self._input_priority = value
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_sides = {"left", "right"}
            if value not in valid_sides:
                raise InvalidSideError("'{}'".format(value))
            self._input_priority = value
        else:
            raise TypeError("'input_priority' must be a str or None")

    # =========================================================================

    @property
    def output_priority(self):
        # type: () -> Literal["left", "right", None]
        """
        TODO
        """
        return self._output_priority

    @output_priority.setter
    def output_priority(self, value):
        # type: (Literal["left", "right", None]) -> None
        if value is None:
            self._output_priority = value
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_sides = {"left", "right"}
            if value not in valid_sides:
                raise InvalidSideError("'{}'".format(value))
            self._output_priority = value
        else:
            raise TypeError("'output_priority' must be a str or None")

    # =========================================================================

    @property
    def filter(self):
        """
        Sets the Splitter's filter. Default filter output side is 'left'.
        TODO
        """
        return self._filter

    @filter.setter
    def filter(self, value):
        # type: (str) -> None
        if value is None:
            self._filter = value
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            if value not in items.raw:
                raise InvalidItemError("'{}'".format(value))
            self._filter = value
        else:
            raise TypeError("'filter' must be a str or None")