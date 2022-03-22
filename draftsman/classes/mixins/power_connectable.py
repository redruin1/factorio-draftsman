# power_connectable.py

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import EntityNotPowerConnectableError
from draftsman.utils import dist
from draftsman.warning import ConnectionDistanceWarning
from draftsman.classes.entity import Entity # TODO: should be EntityLike

from schema import SchemaError
import warnings


class PowerConnectableMixin(object):
    """
    TODO
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(PowerConnectableMixin, self).__init__(
            name, similar_entities, **kwargs
        )

        self._power_connectable = True

        if "maximum_wire_distance" in entities.raw[self.name]:
            self._maximum_wire_distance = entities.raw[self.name]["maximum_wire_distance"]
        else:
            self._maximum_wire_distance = entities.raw[self.name]["wire_max_distance"]

        self.neighbours = []
        if "neighbours" in kwargs:
            self.neighbours = kwargs["neighbours"]
            self.unused_args.pop("neighbours")
        self._add_export("neighbours", lambda x: x is not None and len(x) != 0)

    # =========================================================================

    @property
    def maximum_wire_distance(self):
        # type: () -> int
        """
        Read only
        TODO
        """
        return self._maximum_wire_distance

    # =========================================================================

    @property
    def neighbours(self):
        # type: () -> list
        """
        TODO
        """
        return self._neighbours

    @neighbours.setter
    def neighbours(self, value):
        # type: (list) -> None
        if value is None:
            self._neighbours = []
        else:
            try:
                self._neighbours = signatures.NEIGHBOURS.validate(value)
            except SchemaError:
                raise TypeError("Invalid neighbours format")

    # =========================================================================

    def add_power_connection(self, target, side = 1):
        # type: (Entity, int) -> None
        """
        Adds a power wire between this entity and another power-connectable one.
        """
        if not target.power_connectable:
            raise EntityNotPowerConnectableError(target.id)
        if self.dual_power_connectable and target.dual_power_connectable:
            raise Exception("2 dual power connectable entities cannot connect")

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(self.maximum_wire_distance,
                       target.maximum_wire_distance)
        self_pos = [self.position["x"], self.position["y"]]
        target_pos = [target.position["x"], target.position["y"]]
        real_dist = dist(self_pos, target_pos)
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entities ({}) is greater than max ({})"
                .format(real_dist, min_dist),
                ConnectionDistanceWarning,
                stacklevel = 2
            )

        # Only worried about self
        if self.dual_power_connectable: # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in self.connections:
                self.connections[str_side] = []

            entry = {"entity_id": target.id, "wire_id": 0}
            if entry not in self.connections[str_side]:
                self.connections[str_side].append(entry)
        else: # electric pole
            if not target.dual_power_connectable:
                if target.id not in self.neighbours:
                    self.neighbours.append(target.id)

        # Only worried about target
        if target.dual_power_connectable: # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in target.connections:
                target.connections[str_side] = []

            entry = {"entity_id": self.id, "wire_id": 0}
            if entry not in target.connections[str_side]:
                target.connections[str_side].append(entry)
        else: # electric pole
            if not self.dual_power_connectable:
                if self.id not in target.neighbours:
                    target.neighbours.append(self.id)

    def remove_power_connection(self, target, side = 1):
        # type: (Entity, int) -> None
        """
        TODO
        """

        # Only worried about self
        if self.dual_power_connectable: # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": target.id, "wire_id": 0}
            if str_side in self.connections:
                if entry in self.connections[str_side]:
                    self.connections[str_side].remove(entry)
                if len(self.connections[str_side]) == 0:
                    del self.connections[str_side]
        else: # electric pole
            if not target.dual_power_connectable:
                try:
                    self.neighbours.remove(target.id)
                except ValueError:
                    pass

         # Only worried about target
        if target.dual_power_connectable: # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": self.id, "wire_id": 0}
            if str_side in target.connections:
                if entry in target.connections[str_side]:
                    target.connections[str_side].remove(entry)
                if len(target.connections[str_side]) == 0:
                    del target.connections[str_side]
        else: # electric pole
            if not self.dual_power_connectable:
                try:
                    target.neighbours.remove(self.id)
                except ValueError:
                    pass
