# cargo_bay.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import cargo_bays

import attrs


@attrs.define
class CargoBay(Entity):
    """
    An entity which can be added to a :py:class:`.CargoLandingPad` or a
    :py:class:`.SpacePlatformHub` in order to expand its inventory size and the
    amount of cargo pods it can send/recieve at once.
    """

    @property
    def similar_entities(self) -> list[str]:
        return cargo_bays

    # =========================================================================

    __hash__ = Entity.__hash__


CargoBay.add_schema(None, version=(1, 0))

CargoBay.add_schema({"$id": "urn:factorio:entity:cargo-bay"}, version=(2, 0))
