# circuit_connectable.py

from draftsman.classes.association import Association
from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import entities
from draftsman.signatures import DraftsmanBaseModel, Connections

from pydantic import (
    Field,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from typing import Any, Optional


class CircuitConnectableMixin:
    """
    Enables the Entity to be connected to circuit networks.
    """

    class Format(DraftsmanBaseModel):
        connections: Optional[Connections] = Field(
            Connections(),
            description="""
            All circuit and copper wire connections that this entity has. Note
            that copper wire connections in this field are exclusively for 
            power-switch connections; for power-pole to power-pole connections 
            see the 'neighbours' key.
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.connections = kwargs.get("connections", {})

    # =========================================================================

    @property
    def circuit_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        """
        The maximum distance that this entity can reach for circuit connections.
        Returns ``None`` if the entity's name is not recognized by Draftsman.
        Not exported; read only.
        """
        return entities.raw.get(self.name, {"circuit_wire_max_distance": None}).get(
            "circuit_wire_max_distance", 0
        )

    # =========================================================================

    @property
    def connections(self) -> Connections:
        """
        Connections dictionary. Primarily holds information about the Entity's
        circuit connections (as well as copper wire connections).

        :exception DataFormatError: If set to anything that does not match the
            format of :py:data:`draftsman.signatures.CONNECTIONS`.
        """
        return self._root.connections

    @connections.setter
    def connections(self, value: Connections):
        test_replace_me(
            self,
            type(self).Format,
            self._root,
            "connections",
            value,
            self.validate_assignment,
        )
        # if self.validate_assignment:
        #     result = attempt_and_reissue(
        #         self, type(self).Format, self._root, "connections", value
        #     )
        #     self._root.connections = result
        # else:
        #     self._root.connections = value

    def merge(self, other: Format):
        super().merge(other)

        def merge_circuit_connection(self, side, color, point, other):
            # Keep track of whether or not this association was added to self
            association_added = False

            # Make sure we don't add the same association multiple times
            if point not in self.connections[side][color]:
                self.connections[side][color].append(point)
                association_added = True

            print(point)
            # Determine the location where `point` points to
            association = point["entity_id"]
            associated_entity = association()
            target_side = point.get("circuit_id", 1)  # default to `1` if not there
            if associated_entity.dual_circuit_connectable:
                target = {"entity_id": Association(self), "circuit_id": target_side}
            else:
                target = {"entity_id": Association(self)}

            print(target_side, color)
            target_location = associated_entity.connections[str(target_side)][color]
            for point in target_location:
                if point["entity_id"] == Association(other):
                    if target not in target_location and association_added:
                        point["entity_id"] = Association(self)
                    else:
                        target_location.remove(point)

        # Okay, so merging power connections is not guaranteed to even have a
        # consistent result, due to the fact that they're one-directional by
        # nature
        # Thus, for now at least, I'm going to just flat out prevent users from
        # merging power-switches until I figure out some way to manage this
        # issue

        # def merge_power_connection(self, side, point, other):
        #     # Make sure we don't add the same association multiple times
        #     # point["entity_id"] = Association(self)
        #     # target = {"entity_id": Association(self), "wire_id": 0}

        #     # if point["entity_id"] == Association(other):
        #     #     if target not in self.connections[side]:
        #     #         self.connections[side].append(point)
        #     #     else:
        #     #         point["entity_id"] = Association(self)

        #     association = point["entity_id"]
        #     associated_entity = association()
        #     if associated_entity:
        #         print("bruh")

        # Connections (union of the two sets)
        # TODO: make this way clearer and better, ever since the structure
        # change this is balls
        # Most importantly, develop a standard in regards to supporing pydantic
        # BaseModels and/or raw dictionary values
        for side in other.connections.export_key_values():
            print(side)
            if other.connections[side] is None:
                continue
            # if other.connections[side] is not None:
            if side in {"1", "2"}:
                # if self.connections[side] is None:
                #     self.connections[side] = Connections.CircuitConnections()
                for color, _ in other.connections[side]:
                    if other.connections[side][color] is None:
                        continue
                    if self.connections[side][color] is None:
                        self.connections[side][color] = []
                    for point in other.connections[side][color]:
                        merge_circuit_connection(self, side, color, point, other)
            else:  # side in {"Cu0", "Cu1"}:
                # if side not in self.connections:
                #     self.connections[side] = []
                # for point in other.connections[side]:
                #     if point not in self.connections[side]:
                #         self.connections[side].append(point)
                #     merge_power_connection(self, side, point, other)
                raise ValueError(
                    "Cannot merge power switches (yet); see function for details"
                )

    def to_dict(self, exclude_none: bool = True, exclude_defaults: bool = True) -> dict:
        result = super().to_dict(exclude_none, exclude_defaults)
        if "connections" in result and result["connections"] == {}:
            del result["connections"]
        return result

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.connections == other.connections
