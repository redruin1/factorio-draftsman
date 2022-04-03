# circuit_connectable.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import (
    InvalidWireTypeError,
    InvalidConnectionSideError,
    EntityNotCircuitConnectableError,
)
from draftsman.warning import ConnectionSideWarning, ConnectionDistanceWarning
from draftsman.classes.entity import EntityLike
from draftsman.utils import dist

from schema import SchemaError
import warnings


class CircuitConnectableMixin(object):
    """
    Enables the entity to be connected to circuit networks.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(CircuitConnectableMixin, self).__init__(name, similar_entities, **kwargs)

        self._circuit_connectable = True

        # self.circuit_wire_max_distance = circuit_wire_distances[name]
        # self.circuit_wire_max_distance
        # if not hasattr(self, "circuit_wire_max_distance"):
        #     self.circuit_wire_max_distance = self.maximum_wire_distance
        if "circuit_wire_max_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "circuit_wire_max_distance"
            ]
        elif "maximum_wire_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "maximum_wire_distance"
            ]
        elif "wire_max_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "wire_max_distance"
            ]

        self.connections = {}
        if "connections" in kwargs:
            self.connections = kwargs["connections"]
            self.unused_args.pop("connections")
        self._add_export("connections", lambda x: len(x) != 0)

    # =========================================================================

    @property
    def circuit_wire_max_distance(self):
        # type: () -> int
        """
        Read only
        """
        return self._circuit_wire_max_distance

    # =========================================================================

    @property
    def connections(self):
        # type: () -> dict
        """
        TODO
        """
        return self._connections

    @connections.setter
    def connections(self, value):
        # type: (dict) -> None
        try:
            self._connections = signatures.CONNECTIONS.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid connections format")

    # =========================================================================

    def add_circuit_connection(self, color, target, source_side=1, target_side=1):
        # type: (str, EntityLike, int, int) -> None
        """
        Adds a connection between this entity and `other_entity`

        NOTE: this function only modifies the current entity; for completeness
        you should also connect the other entity to this one.
        """
        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if not isinstance(target, EntityLike):
            raise TypeError("'target' is not an EntityLike")
        if self.id is None or target.id is None:
            raise ValueError("both entities must have a valid id to connect")
        if source_side not in {1, 2}:
            raise InvalidConnectionSideError(source_side)
        if target_side not in {1, 2}:
            raise InvalidConnectionSideError(target_side)

        if not target.circuit_connectable:
            raise EntityNotCircuitConnectableError(target.name)

        if source_side == 2 and not self.dual_circuit_connectable:
            warnings.warn(
                "'source_side' was specified as 2, but entity '{}' is not"
                " dual circuit connectable".format(type(self).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )
        if target_side == 2 and not target.dual_circuit_connectable:
            warnings.warn(
                "'target_side' was specified as 2, but entity '{}' is not"
                " dual circuit connectable".format(type(target).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(self.circuit_wire_max_distance, target.circuit_wire_max_distance)
        self_pos = [self.position["x"], self.position["y"]]
        target_pos = [target.position["x"], target.position["y"]]
        real_dist = dist(self_pos, target_pos)
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entities ({}) is greater than max ({})".format(
                    real_dist, min_dist
                ),
                ConnectionDistanceWarning,
                stacklevel=2,
            )

        # Add target to self.connections

        if str(source_side) not in self.connections:
            self.connections[str(source_side)] = dict()
        current_side = self.connections[str(source_side)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # If dual circuit connectable specify the target side
        if target.dual_circuit_connectable:
            entry = {"entity_id": target.id, "circuit_id": target_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": target.id}

        if entry not in current_color:
            current_color.append(entry)

        # Add self to target.connections

        if str(target_side) not in target.connections:
            target.connections[str(target_side)] = dict()
        current_side = target.connections[str(target_side)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # If dual circuit connectable specify the target side
        if self.dual_circuit_connectable:
            entry = {"entity_id": self.id, "circuit_id": source_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": self.id}

        if entry not in current_color:
            current_color.append(entry)

    def remove_circuit_connection(self, color, target, source_side=1, target_side=1):
        # type: (str, EntityLike, int, int) -> None
        """
        Removes a connection point between this entity and `target`.
        """
        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if not isinstance(target, EntityLike):
            raise TypeError("'target' is not an EntityLike")
        if self.id is None or target.id is None:
            raise ValueError("both entities must have a valid id to connect")
        if source_side not in {1, 2}:
            raise InvalidConnectionSideError(source_side)
        if target_side not in {1, 2}:
            raise InvalidConnectionSideError(target_side)

        # Remove from source
        if target.dual_circuit_connectable:
            entry = {"entity_id": target.id, "circuit_id": target_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": target.id}

        try:
            current_side = self.connections[str(source_side)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from source if applicable
            if len(current_color) == 0:
                del self.connections[str(source_side)][color]
            if len(current_side) == 0:
                del self.connections[str(source_side)]
        except (KeyError, ValueError):
            pass

        # Remove from target
        if self.dual_circuit_connectable:
            entry = {"entity_id": self.id, "circuit_id": source_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": self.id}

        try:
            current_side = target.connections[str(target_side)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from target if applicable
            if len(current_color) == 0:
                del target.connections[str(target_side)][color]
            if len(current_side) == 0:
                del target.connections[str(target_side)]
        except (KeyError, ValueError):
            pass
