# player_port.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import player_ports

import attrs


@attrs.define
class PlayerPort(Entity):
    """
    A constructable respawn point typically used in scenarios.
    """

    @property
    def similar_entities(self) -> list[str]:
        return player_ports

    # =========================================================================

    __hash__ = Entity.__hash__


PlayerPort.add_schema({"$id": "urn:factorio:entity:player-port"}, version=(1, 0))

PlayerPort.add_schema(None, version=(2, 0))
