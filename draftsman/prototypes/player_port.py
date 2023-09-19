# player_port.py

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data import entities
from draftsman.data.entities import player_ports

import warnings


class PlayerPort(Entity):
    """
    A constructable respawn point typically used in scenarios.
    """

    _exports = {}
    _exports.update(Entity._exports)

    def __init__(self, name=player_ports[0], **kwargs):
        # type: (str, **dict) -> None
        super(PlayerPort, self).__init__(name, player_ports, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
