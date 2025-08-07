# circuit_connectable.py

from draftsman.classes.exportable import Exportable
from draftsman.classes.association import Association
from draftsman.data import entities, qualities
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitConnectableMixin(Exportable):
    """
    Enables the Entity to be connected to circuit networks.
    """

    @property
    def circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        """
        The maximum distance that this entity can reach for circuit connections,
        modified based on the entity's :py:attr:`.quality`. If the ``quality``
        is unknown, the distance falls back to the default max distance.

        Returns ``None`` if the entity's name is not recognized under the
        current environment.
        """
        wire_max_dist = entities.raw.get(self.name, {}).get(
            "circuit_wire_max_distance", None
        )
        if wire_max_dist is None:
            return None
        multiplier = 2 * qualities.raw.get(self.quality, {"level": 0})["level"]
        return wire_max_dist + wire_max_dist * multiplier

    # =========================================================================

    _connections: dict = attrs.field(
        factory=dict,
        repr=False,
        alias="connections",
        validator=instance_of(dict),
    )

    @property
    def connections(self) -> dict:
        """
        .. deprecated:: 3.0.0 (Factorio 2.0)

            This information is now converted and stored in
            :py:attr:`.Blueprint.wires`.

        .. serialized::

            This attribute is imported/exported from blueprint strings.

        Connections dictionary. Primarily holds information about the Entity's
        circuit connections, as well as the copper wire connections into/out of
        :py:class:`.PowerSwitch`.

        Historically, power connections between power poles were retained in the
        :py:attr:`~.PowerConnectableMixin.neighbours` attribute - but this
        attribute is also deprecated in favor of :py:attr:`.Blueprint.wires`.
        """
        return self._connections

    # =========================================================================

    def merge(self, other: "CircuitConnectableMixin"):
        super().merge(other)

        # We know that `other` is being merged on top of `self`, such that `other` will be deleted
        # Thus any wires that point to `other` now need to point to `self`
        # Wires that point to `other` can only exist in `other.wires`
        # All we want to do is change the association to `other` in `other.wires`
        # to be an association to `self` in `other.wires`
        # If there are any duplicate wires, they (currently) get omitted during
        # dictionary resolution (to_dict())
        if other.parent is not None:
            for wire in other.parent.wires:
                if wire[0]() is other:
                    wire[0] = Association(self)
                if wire[2]() is other:
                    wire[2] = Association(self)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    CircuitConnectableMixin,
    lambda fields: {
        "connections": fields._connections.name,
    },
    lambda fields, converter: {
        "connections": fields._connections.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    CircuitConnectableMixin,
    lambda fields: {
        "connections": fields._connections.name,
    },
    lambda fields, converter: {"connections": None},
)
