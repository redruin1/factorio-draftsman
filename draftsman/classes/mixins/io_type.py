# io_type.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.error import DataFormatError
from draftsman import signatures

from schema import SchemaError
import six

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity

try:
    from typing import Literal
except ImportError:  # pragma: no coverage
    from typing_extensions import Literal


class IOTypeMixin(object):
    """
    Gives an entity a Input/Output type.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(IOTypeMixin, self).__init__(name, similar_entities, **kwargs)

        self.io_type = "input"  # Default
        # Import dict (internal) format
        if "type" in kwargs:
            self.io_type = kwargs["type"]
            self.unused_args.pop("type")
        # More user-friendly format in line with attribute name
        elif "io_type" in kwargs:
            self.io_type = kwargs["io_type"]
            self.unused_args.pop("io_type")

        self._add_export(
            "io_type",
            lambda x: x is not None and x != "input",
            lambda k, v: ("type", v),
        )

    # =========================================================================

    @property
    def io_type(self):
        # type: () -> Literal["input", "output", None]
        """
        Whether this entity is set to recieve or send items. Used to
        differentiate between input and output underground belts, as well as
        whether or not a loader inserts or removes items from an adjacent
        container. Can be one of ``"input"``, ``"output"``, or ``None``.

        :getter: Sets the input/output type of the Entity.
        :setter: Gets the input/output type of the Entity.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception ValueError: If set to anything other than ``"input"`` or
            ``"output"``.
        """
        return self._io_type

    @io_type.setter
    def io_type(self, value):
        # type: (Literal["input", "output", None]) -> None
        try:
            value = signatures.STRING_OR_NONE.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if value in {"input", "output", None}:
            self._io_type = value
        else:
            raise ValueError("'io_type' must be 'input', 'output' or None")

    # =========================================================================

    def merge(self, other):
        # type: (Entity) -> None
        super(IOTypeMixin, self).merge(other)

        self.io_type = other.io_type
