# linked_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import InventoryMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import uint32
from draftsman.validators import instance_of

from draftsman.data.entities import linked_containers

import attrs


@attrs.define
class LinkedContainer(InventoryMixin, Entity):
    """
    An entity that allows sharing it's contents with any other ``LinkedContainer``
    with the same ``link_id``.
    """

    @property
    def similar_entities(self) -> list[str]:
        return linked_containers

    # =========================================================================

    def _only_use_lowest_bits(value):
        if isinstance(value, int):
            return value & 0xFFFFFFFF
        else:
            return value

    link_id: uint32 = attrs.field(
        default=0, converter=_only_use_lowest_bits, validator=instance_of(uint32)
    )
    """
    The linking ID that this ``LinkedContainer`` currently has. Encoded as
    a 32 bit unsigned integer, where a container only links to another with
    the same ``link_id``. If an integer greater than 32-bits is passed in,
    only the lowest bits are used.

    :exception DataFormatError: If set to anything other than an ``uint32``.
    """

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


draftsman_converters.add_hook_fns(
    LinkedContainer,
    lambda fields: {"link_id": fields.link_id.name},
)
