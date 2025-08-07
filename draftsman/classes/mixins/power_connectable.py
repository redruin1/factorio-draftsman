# power_connectable.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities
from draftsman.serialization import draftsman_converters

import attrs


@attrs.define(slots=False)
class PowerConnectableMixin(Exportable):
    """
    Enables the Entity to be connected to power networks.
    """

    @property
    def power_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def maximum_wire_distance(self) -> float:
        """
        The maximum distance that this entity can reach for power connections.
        Returns ``None`` if this entity's name is not recognized by Draftsman.
        """
        return entities.raw.get(self.name, {"maximum_wire_distance": None})[
            "maximum_wire_distance"
        ]

    # =========================================================================

    _neighbours: list[int] = attrs.field(
        factory=list,
        repr=False,
    )

    @property
    def neighbours(self) -> list[int]:
        """
        .. deprecated:: 3.0.0 (Factorio 2.0)

            This information is now converted and stored in the
            :py:attr:`.Blueprint.wires` attribute whenever possible.

        The set of neighbouring power poles that this pole connects to. Limited
        to 5 unique entries, since power poles (pre Factorio 2.0) could only
        have a maximum of 5 connections. Each integer entry in this list
        corresponds to the :py:attr:`.entity_number` of a corresponding entity
        in the same blueprint.
        """
        return self._neighbours


draftsman_converters.get_version((1, 0)).add_hook_fns(
    PowerConnectableMixin,
    lambda fields: {"neighbours": fields._neighbours.name},
    lambda fields, converter: {"neighbours": fields._neighbours.name},
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    PowerConnectableMixin,
    lambda fields: {
        "neighbours": fields._neighbours.name,
    },
    lambda fields, converter: {"neighbours": None},
)
