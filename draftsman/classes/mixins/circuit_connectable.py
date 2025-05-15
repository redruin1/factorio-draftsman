# circuit_connectable.py

from draftsman.classes.exportable import Exportable
from draftsman.classes.association import Association
from draftsman.data import entities
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
        """
        Whether or not this entity can be connected with either red or green
        circuit wires.
        """
        return True

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        """
        The maximum distance that this entity can reach for circuit connections.
        Returns ``None`` if the entity's name is not recognized under the
        current environment. Not exported; read only.
        """
        # TODO: modify this based on quality
        return entities.raw.get(self.name, {"circuit_wire_max_distance": None}).get(
            "circuit_wire_max_distance", 0
        )

    # =========================================================================

    _connections: dict = attrs.field(
        factory=dict,
        repr=False,
        alias="connections",
        validator=instance_of(dict),  # TODO: better validator?
    )

    @property
    def connections(self) -> dict:
        """
        Connections dictionary. Primarily holds information about the Entity's
        circuit connections (as well as copper wire connections).

        Deprecated in Factorio 2.0. On blueprint string import, this field will
        be converted to the blueprint's :py:attr:`.Blueprint.wires` attribute.
        This value is only ever populated when loading from a pre-Factorio 1.0
        entity dictionary with the method :py:meth:`.from_dict`. This is
        provided so that users may manually try and reconstruct wire connections
        with incomplete data, and such that round-trip import/exporting retains
        all given keys.
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

        # TODO: ideally this would happen further up the stack, but thank god I
        # included this parent attribute cause holy shit this is gonna be aids
        # to rewrite


CircuitConnectableMixin.add_schema(
    {
        "$defs": {
            "circuit-connection-point": {
                "type": "object",
                "properties": {
                    "entity_id": {"$ref": "urn:uint64"},
                    "circuit_id": {"enum": [1, 2]},
                },
                "required": ["entity_id"],
            },
            "wire-connection-point": {
                "properties": {
                    "entity_id": {"$ref": "urn:uint64"},
                    "wire_id": {"enum": [0, 1]},
                },
                "required": ["entity_id"],
            },
        },
        "properties": {
            "connections": {
                "type": "object",
                "properties": {
                    "1": {
                        "type": "object",
                        "properties": {
                            "red": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/circuit-connection-point"},
                            },
                            "green": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/circuit-connection-point"},
                            },
                        },
                    },
                    "2": {
                        "type": "object",
                        "properties": {
                            "red": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/circuit-connection-point"},
                            },
                            "green": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/circuit-connection-point"},
                            },
                        },
                    },
                    "Cu0": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/wire-connection-point"},
                    },
                    "Cu1": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/wire-connection-point"},
                    },
                },
            }
        },
    },
    version=(1, 0),
)

CircuitConnectableMixin.add_schema({}, version=(2, 0))

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
