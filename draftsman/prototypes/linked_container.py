# linked_container.py

from draftsman.prototypes.mixins import InventoryMixin, Entity
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import linked_containers

import warnings


class LinkedContainer(InventoryMixin, Entity):
    def __init__(self, name = linked_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(LinkedContainer, self).__init__(name, linked_containers, **kwargs)

        self.link_id = 0
        if "link_id" in kwargs:
            self.set_links(kwargs["link_id"])
            self.unused_args.pop("link_id")
        self._add_export("link_id", lambda x: x != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_links(self, id):
        # type: (int) -> None
        """
        """
        # TODO: assert id in range(0, 2^32-1)
        if id is None:
            self.link_id = 0
        else:
            self.link_id = signatures.INTEGER.validate(id)

    def set_link(self, number, enabled):
        # type: (int, bool) -> None
        """
        """
        assert number < 32
        if enabled:
            self.link_id |= (1 << number)
        else:
            self.link_id &= ~(1 << number)
