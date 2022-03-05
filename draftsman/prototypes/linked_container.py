# linked_container.py

from draftsman.prototypes.mixins import InventoryMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import linked_containers


class LinkedContainer(InventoryMixin, Entity):
    def __init__(self, name: str = linked_containers[0], **kwargs):
        if name not in linked_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LinkedContainer, self).__init__(name, **kwargs)

        self.link_id = 0
        if "link_id" in kwargs:
            self.set_links(kwargs["link_id"])
            self.unused_args.pop("link_id")
        self._add_export("link_id", lambda x: x != 0)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_links(self, id: int) -> None:
        """
        """
        # TODO: assert id in range(0, 2^32-1)
        if id is None:
            self.link_id = 0
        else:
            self.link_id = signatures.INTEGER.validate(id)

    def set_link(self, number: int, enabled: bool) -> None:
        """
        """
        assert number < 32
        if enabled:
            self.link_id |= (1 << number)
        else:
            self.link_id &= ~(1 << number)
