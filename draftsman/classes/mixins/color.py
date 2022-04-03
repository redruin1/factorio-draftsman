# color.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures

from typing import Union
from schema import SchemaError


class ColorMixin(object):
    """
    Gives the entity an editable color. Used on Locomotives and Train Stops.
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
        TODO
        """
        return self._color

    @color.setter
    def color(self, value):
        # type: (Union[list, dict]) -> None
        # TODO: issue a range error if not in range [0, 255]
        try:
            self._color = signatures.COLOR.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid color format")
