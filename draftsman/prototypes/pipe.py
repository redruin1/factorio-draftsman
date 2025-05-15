# pipe.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import pipes

import attrs


@attrs.define
class Pipe(Entity):
    """
    A structure that transports a fluid across a surface.
    """

    @property
    def similar_entities(self) -> list[str]:
        return pipes

    # =========================================================================

    __hash__ = Entity.__hash__


Pipe.add_schema({"$id": "urn:factorio:entity:pipe"})
