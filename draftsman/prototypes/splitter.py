# splitter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.error import InvalidItemError, InvalidSideError
from draftsman.warning import DraftsmanWarning

from draftsman.data import items

from draftsman.data.entities import splitters
from draftsman.data import entities

import six
import warnings

try:
    from typing import Literal
except ImportError:  # pragma: no coverage
    from typing_extensions import Literal


class Splitter(DirectionalMixin, Entity):
    """
    An entity that evenly splits a set of input belts between a set of output
    belts.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **DirectionalMixin._exports,
    #     "input_priority": {
    #         "format": "'left' or 'right'",
    #         "description": "Which side takes input priority",
    #         "required": lambda x: x is not None,
    #     },
    #     "output_priority": {
    #         "format": "'left' or 'right'",
    #         "description": "Which side takes output priority",
    #         "required": lambda x: x is not None,
    #     },
    #     "filter": {
    #         "format": "str",
    #         "description": "Name of the item being filtered",
    #         "required": lambda x: x is not None,
    #     },
    # }
    # fmt: off
    class Format(DirectionalMixin.Format, Entity.Format):
        input_priority: Literal["left", "right"] | None = None
        output_priority: Literal["left", "right"] | None = None
        filter: str | None = None

    def __init__(self, name=splitters[0], **kwargs):
        # type: (str, **dict) -> None
        super(Splitter, self).__init__(name, splitters, **kwargs)

        self.input_priority = None
        if "input_priority" in kwargs:
            self.input_priority = kwargs["input_priority"]
            self.unused_args.pop("input_priority")
        # self._add_export("input_priority", lambda x: x is not None)

        self.output_priority = None
        if "output_priority" in kwargs:
            self.output_priority = kwargs["output_priority"]
            self.unused_args.pop("output_priority")
        # self._add_export("output_priority", lambda x: x is not None)

        self.filter = None
        if "filter" in kwargs:
            self.filter = kwargs["filter"]
            self.unused_args.pop("filter")
        # self._add_export("filter", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    @property
    def input_priority(self):
        # type: () -> Literal["left", "right", None]
        """
        The input priority of the ``Splitter``. Can be one of ``"left"`` or
        ``"right"``.

        :getter: Gets the input priority.
        :setter: Sets the input priority.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidSideError: If set to an invalid side as specified
            above.
        """
        return self._root.get("input_priority", None)

    @input_priority.setter
    def input_priority(self, value):
        # type: (Literal["left", "right", None]) -> None
        if value is None:
            self._root.pop("input_priority", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_sides = {"left", "right"}
            if value not in valid_sides:
                raise InvalidSideError("'{}'".format(value))
            self._root["input_priority"] = value
        else:
            raise TypeError("'input_priority' must be a str or None")

    # =========================================================================

    @property
    def output_priority(self):
        # type: () -> Literal["left", "right", None]
        """
        The outpu priority of the ``Splitter``. Can be one of ``"left"`` or
        ``"right"``.

        :getter: Gets the output priority.
        :setter: Sets the output priority.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidSideError: If set to an invalid side as specified
            above.
        """
        return self._root.get("output_priority", None)

    @output_priority.setter
    def output_priority(self, value):
        # type: (Literal["left", "right", None]) -> None
        if value is None:
            self._root.pop("output_priority", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            valid_sides = {"left", "right"}
            if value not in valid_sides:
                raise InvalidSideError("'{}'".format(value))
            self._root["output_priority"] = value
        else:
            raise TypeError("'output_priority' must be a str or None")

    # =========================================================================

    @property
    def filter(self):
        """
        Sets the Splitter's filter. If ``filter`` is set but ``output_priority``
        is not, then the output side defaults to ``"left"``.

        :getter: Gets the splitter's item filter.
        :setter: Sets the splitter's item filter.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidItemError: If set to an invalid item name.
        """
        return self._root.get("filter", None)

    @filter.setter
    def filter(self, value):
        # type: (str) -> None
        if value is None:
            self._root.pop("filter", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            if value not in items.raw:
                raise InvalidItemError("'{}'".format(value))
            self._root["filter"] = value
        else:
            raise TypeError("'filter' must be a str or None")

    # =========================================================================

    def merge(self, other):
        # type: (Splitter) -> None
        super(Splitter, self).merge(other)

        self.input_priority = other.input_priority
        self.output_priority = other.output_priority
        self.filter = other.filter

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and 
            self.input_priority == other.input_priority and
            self.output_priority == other.output_priority and
            self.filter == other.filter
        )
