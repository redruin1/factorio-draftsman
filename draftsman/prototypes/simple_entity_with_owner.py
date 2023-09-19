# simple_entity_with_owner.py

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data import entities
from draftsman.data.entities import simple_entities_with_owner

import warnings


class SimpleEntityWithOwner(Entity):
    """
    A generic entity owned by some other entity.
    """

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(
        {
            "variation": {
                "format": "int",
                "description": "Graphical variation of the entity",
                "required": lambda x: x is not None,
            },
        }
    )

    def __init__(self, name=simple_entities_with_owner[0], **kwargs):
        # type: (str, **dict) -> None
        super(SimpleEntityWithOwner, self).__init__(
            name, simple_entities_with_owner, **kwargs
        )

        self.variation = 1
        if "variation" in kwargs:
            self.variation = kwargs["variation"]
            self.unused_args.pop("variation")

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    @property
    def variation(self):
        # type: () -> int
        """
        The number representing the graphical variation of the entity.

        :type: ``int``
        """
        return self._variation

    @variation.setter
    def variation(self, value):
        # type: (int) -> None
        self._variation = value
