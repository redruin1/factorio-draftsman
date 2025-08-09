# player_port.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import player_ports

import attrs


@attrs.define
class PlayerPort(Entity):
    """
    A constructable respawn point typically used in scenarios.

    .. deprecated:: 2.0 (Factorio)
    """

    @property
    def similar_entities(self) -> list[str]:
        return player_ports

    # =========================================================================

    __hash__ = Entity.__hash__
