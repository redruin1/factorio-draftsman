# simple_entity_with_force.py

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data import entities
from draftsman.data.entities import simple_entities_with_force

import warnings


class SimpleEntityWithForce(Entity):
    """
    A generic entity associated with a team of players.
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

    def __init__(self, name=simple_entities_with_force[0], **kwargs):
        # type: (str, **dict) -> None
        super(SimpleEntityWithForce, self).__init__(
            name, simple_entities_with_force, **kwargs
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
