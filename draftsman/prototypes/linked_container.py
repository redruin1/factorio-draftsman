# linked_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import InventoryMixin, RequestItemsMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint16, uint32

from draftsman.data.entities import linked_containers

from pydantic import ConfigDict, Field, field_validator
from typing import Any, Literal, Optional, Union


class LinkedContainer(InventoryMixin, RequestItemsMixin, Entity):
    """
    An entity that allows sharing it's contents with any other ``LinkedContainer``
    with the same ``link_id``.
    """

    class Format(
        InventoryMixin.Format,
        RequestItemsMixin.Format,
        Entity.Format,
    ):
        link_id: Optional[uint32] = Field(
            0,
            description="""
            A unique integer key that this container will broadcast it's 
            contents on.
            """,
        )

        @field_validator("link_id", mode="before")
        @classmethod
        def only_use_lowest_bits(cls, value: Any):
            if isinstance(value, int):
                return value & 0xFFFFFFFF
            else:
                return value

        model_config = ConfigDict(title="LinkedContainer")

    def __init__(
        self,
        name: str = linked_containers[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        link_id: uint32 = 0,
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format

        super().__init__(
            name,
            linked_containers,
            position=position,
            tile_position=tile_position,
            bar=bar,
            items=items,
            tags=tags,
            **kwargs
        )

        self.link_id = link_id

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def link_id(self) -> Optional[uint32]:
        """
        The linking ID that this ``LinkedContainer`` currently has. Encoded as
        a 32 bit unsigned integer, where a container only links to another with
        the same ``link_id``. If an integer greater than 32-bits is passed in,
        only the lowest bits are used.

        :getter: Gets the link ID of the ``LinkedContainer``.
        :setter: Sets the link ID of the ``LinkedContainer``.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or ``None``.
        """
        return self._root.link_id

    @link_id.setter
    def link_id(self, value: Optional[uint32]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self, type(self).Format, self._root, "link_id", value
            )

        if value is None:
            self._root.link_id = 0
        else:
            self._root.link_id = value

    # =========================================================================

    def set_link(self, number: int, enabled: bool):
        """
        Set a single "link point". Corresponds to flipping a single bit in
        ``link_id``.

        :param number: Which bit to flip in ``link_id``.
        :param enabled: Whether or not to set it to ``1`` or to ``0``.

        :exception AssertionError: If ``number`` is not in the range ``[0, 32)``.
        """
        number = int(number)
        enabled = bool(enabled)

        if not 0 <= number < 32:
            raise ValueError("'number' must be in the range [0, 32)")

        if enabled:
            self.link_id |= 1 << number
        else:
            self.link_id &= ~(1 << number)

    def merge(self, other: "LinkedContainer"):
        super(LinkedContainer, self).merge(other)

        self.link_id = other.link_id

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other: "LinkedContainer") -> bool:
        return super().__eq__(other) and self.link_id == other.link_id
