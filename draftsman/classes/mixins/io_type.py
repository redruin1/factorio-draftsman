# io_type.py

# TODO: make this an enum?

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters

import attrs
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class IOTypeMixin:
    """
    Gives an entity a Input/Output type.
    """

    class Format(BaseModel):
        io_type: Optional[Literal["input", "output"]] = Field(
            "input",
            alias="type",
            description="""
            The input/output type of the entity. Used on Loaders and Underground
            Belts to indicate what direction this entity is working.
            """,
        )

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.io_type = "input"  # Default
    #     # Import dict (internal) format
    #     if "type" in kwargs:
    #         self.io_type = kwargs["type"]
    #     # More user-friendly format in line with attribute name
    #     else:  # "io_type" in kwargs:
    #         self.io_type = kwargs["io_type"]

    # =========================================================================

    io_type: Literal["input", "output", None] = attrs.field(
        default="input",
        # TODO: validators
    )
    """
    Whether this entity is set to recieve or send items. Used to
    differentiate between input and output underground belts/pipes, as well as
    whether or not a loader inserts or removes items from an adjacent
    container. Can be one of ``"input"`` or ``"output"``.
    """

    @io_type.validator
    def io_type_validator(self, attr, value, mode: Optional[ValidationMode] = None):
        mode = mode if mode is not None else self.validate_assignment
        if mode:
            if value not in {"input", "output"}:
                msg = "'{}' was given {}; must be either 'input' or 'output'".format(
                    attr.name, repr(value)
                )
                raise DataFormatError(msg)

    # @property
    # def io_type(self) -> Literal["input", "output", None]:
    #     """
    #     Whether this entity is set to recieve or send items. Used to
    #     differentiate between input and output underground belts, as well as
    #     whether or not a loader inserts or removes items from an adjacent
    #     container. Can be one of ``"input"``, ``"output"``, or ``None``.

    #     :getter: Sets the input/output type of the Entity.
    #     :setter: Gets the input/output type of the Entity.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception ValueError: If set to anything other than ``"input"`` or
    #         ``"output"``.
    #     """
    #     return self._root.io_type

    # @io_type.setter
    # def io_type(self, value: Literal["input", "output", None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "io_type", value
    #         )
    #         self._root.io_type = result
    #     else:
    #         self._root.io_type = value

    # =========================================================================

    def merge(self, other: "IOTypeMixin"):
        super().merge(other)

        self.io_type = other.io_type

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.io_type == other.io_type


draftsman_converters.add_schema(
    {"$id": "factorio:io_type_mixin"},
    IOTypeMixin,
    lambda fields: {"type": fields.io_type.name},
)
