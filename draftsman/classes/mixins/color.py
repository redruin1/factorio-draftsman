# color.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.error import DataFormatError
from draftsman import signatures

from typing import Union
from schema import SchemaError
import six


class ColorMixin(object):
    """
    Gives the entity an editable color.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(ColorMixin, self).__init__(name, similar_entities, **kwargs)

        self.color = None
        if "color" in kwargs:
            self.color = kwargs["color"]
            self.unused_args.pop("color")
        self._add_export("color", lambda x: x is not None)

    @property
    def color(self):
        # type: () -> dict
        """
        The color of the Entity.

        The ``color`` attribute exists in a dict format with the "r", "g",
        "b", and an optional "a" keys. The color can be specified like that, or
        it can be specified more succinctly as a sequence of 3-4 numbers,
        representing the colors in that order.

        The value of each of the numbers (according to Factorio spec) can be
        either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
        <= 1.0, the former range is used, and the latter otherwise. If "a" is
        omitted, it defaults to 1.0 or 255 when imported, depending on the
        range of the other numbers.

        :getter: Gets the color of the Entity, or ``None`` if not set.
        :setter: Sets the color of the Entity.
        :type: ``dict{"r": float, "g": float, "b": float, Optional("a"): float}``

        :exception DataFormatError: If the set ``color`` does not match the
            above specification.
        """
        return self._color

    @color.setter
    def color(self, value):
        # type: (Union[list, dict]) -> None
        try:
            self._color = signatures.COLOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
