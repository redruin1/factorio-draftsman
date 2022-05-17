# linked_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import InventoryMixin, RequestItemsMixin
from draftsman import signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import linked_containers

import six
import warnings


class LinkedContainer(InventoryMixin, RequestItemsMixin, Entity):
    """
    An entity that allows sharing it's contents with any other ``LinkedContainer``
    with the same ``link_id``.
    """

    def __init__(self, name=linked_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(LinkedContainer, self).__init__(name, linked_containers, **kwargs)

        self.link_id = 0
        if "link_id" in kwargs:
            self.link_id = kwargs["link_id"]
            self.unused_args.pop("link_id")
        self._add_export("link_id", lambda x: x != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def link_id(self):
        # type: () -> int
        """
        The linking ID that this ``LinkedContainer`` currently has. Encoded as
        a 32 bit unsigned integer, where a container only links to another with
        the same ``link_id``. If an integer greater than 32-bits is passed in
        only the lowest bits are used.

        :getter: Gets the link ID of the ``LinkedContainer``.
        :setter: Sets the link ID of the ``LinkedContainer``.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or ``None``.
        """
        return self._link_id

    @link_id.setter
    def link_id(self, value):
        # type: (int) -> None
        if value is None:
            self._link_id = 0
        elif isinstance(value, six.integer_types):
            self._link_id = value & 0xFFFFFFFF
        else:
            raise TypeError("'link_id' must be an int or None")

    # =========================================================================

    def set_link(self, number, enabled):
        # type: (int, bool) -> None
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
