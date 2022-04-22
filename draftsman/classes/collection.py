# collection.py

from draftsman.classes.entitylike import EntityLike
from draftsman.classes.tile import Tile
from draftsman.error import (
    DraftsmanError,
    EntityNotPowerConnectableError,
    InvalidWireTypeError,
    InvalidConnectionSideError,
    EntityNotCircuitConnectableError,
)
from draftsman.warning import (
    ConnectionSideWarning,
    ConnectionDistanceWarning,
    TooManyConnectionsWarning,
)
from draftsman import utils

import abc
import six
import warnings


@six.add_metaclass(abc.ABCMeta)
class EntityCollection(object):
    """
    Abstract class used for other constructs that can contain EntityLikes, such
    as Group and Blueprint.
    """

    # =========================================================================
    # Properties
    # =========================================================================

    @abc.abstractproperty
    def entities(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def entity_hashmap(self):  # pragma: no coverage
        pass

    # TODO: utilize
    # @property
    # def flippable(self):
    #     # type: () -> bool
    #     """
    #     Read only
    #     """
    #     for entity in self.entities:
    #         if not entity.flippable:
    #             return False

    #     return True

    # =========================================================================
    # Custom edge functions for EntityList interaction
    # =========================================================================

    def on_entity_insert(self, entitylike):  # pragma: no coverage
        # type: (EntityLike) -> None
        pass

    def on_entity_set(self, old_entitylike, new_entitylike):  # pragma: no coverage
        # type: (EntityLike, EntityLike) -> None
        pass

    def on_entity_remove(self, entitylike):  # pragma: no coverage
        # type: (EntityLike) -> None
        pass

    # =========================================================================
    # Queries
    # =========================================================================

    def find_entity(self, name, position):
        # type: (str, tuple) -> EntityLike
        """
        Finds an entity with `name` at a grid position `position`.
        """
        results = self.entity_hashmap.get_on_point(position)
        try:
            return list(filter(lambda x: x.name == name, results))[0]
        except IndexError:
            return None

    def find_entities(self, aabb=None):
        # type: (list) -> list[EntityLike]
        """
        Returns a list of all entities within the area `aabb`. Works similiarly
        to `LuaSurface.find_entities`. If no `aabb` is provided then the
        function simply returns all the entities in the blueprint.
        """
        if aabb is None:
            return list(self.entities)

        return self.entity_hashmap.get_in_area(aabb)

    def find_entities_filtered(self, **kwargs):
        # type: (**dict) -> list[EntityLike]
        """
        Returns a filtered list of entities within the `Collection`. Works
        similarly to `LuaSurface.find_entities_filtered`.

        Possible keywords include:
        * area: AABB to search in
        * position: grid position to search
        * radius: radius around position to search in
        * name: name or set of names, only entities with those names will be
        returned
        * type: type or set of types, only entities of those types will be
        returned
        * direction: direction or set of directions, only entities facing those
        directions will be returned
        * limit: maximum number of entities to return
        * invert: Boolean, whether or not to invert the search selection
        """

        search_region = []
        if "position" in kwargs:
            if "radius" in kwargs:
                # Intersect entities with circle
                search_region = self.entity_hashmap.get_in_radius(
                    kwargs["radius"], kwargs["position"]
                )
            else:
                # Intersect entities with point
                search_region = self.entity_hashmap.get_on_point(kwargs["position"])
        elif "area" in kwargs:
            # Intersect entities with area
            search_region = self.entity_hashmap.get_in_area(kwargs["area"])
        else:
            search_region = self.entities

        if isinstance(kwargs.get("name", None), str):
            names = {kwargs.pop("name", None)}
        else:
            names = kwargs.pop("name", None)
        if isinstance(kwargs.get("type", None), str):
            types = {kwargs.pop("type", None)}
        else:
            types = kwargs.pop("type", None)
        if isinstance(kwargs.get("direction", None), int):
            directions = {kwargs.pop("direction", None)}
        else:
            directions = kwargs.pop("direction", None)

        # Keep track of how many
        limit = kwargs.pop("limit", len(search_region))

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            if types is not None and entity.type not in types:
                return False
            if (
                directions is not None
                and getattr(entity, "direction", None) not in directions
            ):
                return False
            return True

        if kwargs.get("invert", None):
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]

    # =========================================================================
    # Connections
    # =========================================================================

    def add_power_connection(self, id1, id2, side=1):
        # type: (str, str, int) -> None
        """
        Adds a copper wire power connection between two entities. Side specifies
        which side to connect to when establishing a connection to a dual-power-
        connectable entity (usually a power-switch).

        .. NOTE:

            `side` is in 1-based notation (1 and 2, input and output) which is
            identical to circuit connections, though internally the connections
            are represented in 0-based notation as "Cu0" and "Cu1" respectively.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        if not entity_1.power_connectable:
            raise EntityNotPowerConnectableError(entity_1.name)
        if not entity_2.power_connectable:
            raise EntityNotPowerConnectableError(entity_2.name)
        if entity_1.dual_power_connectable and entity_2.dual_power_connectable:
            raise DraftsmanError(
                "2 dual-power-connectable entities cannot connect directly"
            )

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(entity_1.maximum_wire_distance, entity_2.maximum_wire_distance)
        entity_1_pos = [entity_1.position["x"], entity_1.position["y"]]
        entity_2_pos = [entity_2.position["x"], entity_2.position["y"]]
        real_dist = utils.dist(entity_1_pos, entity_2_pos)
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entities ({}) is greater than max connection distance"
                " ({})".format(real_dist, min_dist),
                ConnectionDistanceWarning,
                stacklevel=2,
            )

        # Issue a warning if the either of the connected entities have 5 or more
        # power connections
        if len(entity_1.neighbours) >= 5:
            warnings.warn(
                "'entity_1' ({}) has more than 5 connections".format(entity_1.name),
                TooManyConnectionsWarning,
                stacklevel=2,
            )
        if len(entity_2.neighbours) >= 5:
            warnings.warn(
                "'entity_2' ({}) has more than 5 connections".format(entity_2.name),
                TooManyConnectionsWarning,
                stacklevel=2,
            )

        # Only worried about self
        if entity_1.dual_power_connectable:  # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in entity_1.connections:
                entity_1.connections[str_side] = []

            entry = {"entity_id": entity_2, "wire_id": 0}
            if entry not in entity_1.connections[str_side]:
                entity_1.connections[str_side].append(entry)
        else:  # electric pole
            if not entity_2.dual_power_connectable:
                if entity_2 not in entity_1.neighbours:
                    entity_1.neighbours.append(entity_2)

        # Only worried about target
        if entity_2.dual_power_connectable:  # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in entity_2.connections:
                entity_2.connections[str_side] = []

            entry = {"entity_id": entity_1, "wire_id": 0}
            if entry not in entity_2.connections[str_side]:
                entity_2.connections[str_side].append(entry)
        else:  # electric pole
            if not entity_1.dual_power_connectable:
                if entity_1 not in entity_2.neighbours:
                    entity_2.neighbours.append(entity_1)

    def remove_power_connection(self, id1, id2, side=1):
        # type: (str, str, int) -> None
        """
        Removes a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        # Only worried about self
        if entity_1.dual_power_connectable:  # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": entity_2, "wire_id": 0}
            if str_side in entity_1.connections:
                if entry in entity_1.connections[str_side]:
                    entity_1.connections[str_side].remove(entry)
                if len(entity_1.connections[str_side]) == 0:
                    del entity_1.connections[str_side]
        else:  # electric pole
            if not entity_2.dual_power_connectable:
                try:
                    entity_1.neighbours.remove(entity_2)
                except ValueError:
                    pass

        # Only worried about target
        if entity_2.dual_power_connectable:  # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": entity_1, "wire_id": 0}
            if str_side in entity_2.connections:
                if entry in entity_2.connections[str_side]:
                    entity_2.connections[str_side].remove(entry)
                if len(entity_2.connections[str_side]) == 0:
                    del entity_2.connections[str_side]
        else:  # electric pole
            if not entity_1.dual_power_connectable:
                try:
                    entity_2.neighbours.remove(entity_1)
                except ValueError:
                    pass

    def remove_power_connections(self):
        # type: () -> None
        """
        Remove all power connections in the Collection.
        TODO: handle power switches
        """
        for entity in self.entities:
            if hasattr(entity, "neighbours"):
                entity.neighbours = None

    def generate_power_connections(self, prefer_axis=True, only_axis=False):
        # type: (bool, bool) -> None
        """
        Automatically create power connections between all electric poles.

        The algorithm used is similar to demi-pixel's
        `generateElectricalConnections()` (https://github.com/demipixel/factorio-blueprint/blob/master/src/electrical-connections.ts)
        but with some slight differences.
        """
        # Get all power poles in the Collection
        electric_poles = self.find_entities_filtered(type="electric-pole")
        for cur_pole in electric_poles:
            # Get all the power poles candidates
            def power_connectable(other):
                # type: (EntityLike) -> bool
                # Don't include ourself in the entities we're connecting to
                if other is cur_pole:
                    return False
                # Don't include poles that we're already connected to
                # TODO
                # If only_axis is true, only include ones that have the same x
                # or y
                if (
                    cur_pole.position["x"] != other.position["x"]
                    and cur_pole.position["y"] != other.position["y"]
                ) and only_axis:
                    return False
                # Only return poles that are less than the max power pole
                # distance
                distance = utils.dist(cur_pole.position, other.position)
                min_dist = min(
                    cur_pole.maximum_wire_distance, other.maximum_wire_distance
                )
                return distance <= min_dist

            potential_neighbours = list(filter(power_connectable, electric_poles))
            # Sort the power poles by distance
            # potential_neighbours.sort(
            #     key = lambda x: utils.dist(x.position, cur_pole.position)
            # )
            potential_neighbours = sorted(
                potential_neighbours,
                key=lambda x: utils.dist(x.position, cur_pole.position),
                reverse=True,
            )
            # Sort the power poles by whether or not they are on the axis first
            if prefer_axis:
                potential_neighbours.sort(
                    key=lambda x: not (
                        x.position["x"] == cur_pole.position["x"]
                        or x.position["y"] == cur_pole.position["y"]
                    )
                )

            cur_index = self.entities.index(cur_pole)
            while len(cur_pole.neighbours) <= 5 and len(potential_neighbours) > 0:
                other_index = self.entities.index(potential_neighbours.pop())
                self.add_power_connection(cur_index, other_index)

    # =========================================================================

    def add_circuit_connection(self, color, id1, id2, side1=1, side2=1):
        # type: (str, str, str, int, int) -> None
        """
        Adds a circuit wire connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side1 not in {1, 2}:
            raise InvalidConnectionSideError(side1)
        if side2 not in {1, 2}:
            raise InvalidConnectionSideError(side2)

        if not entity_1.circuit_connectable:
            raise EntityNotCircuitConnectableError(entity_1.name)
        if not entity_2.circuit_connectable:
            raise EntityNotCircuitConnectableError(entity_2.name)

        if side1 == 2 and not entity_1.dual_circuit_connectable:
            warnings.warn(
                "'side1' was specified as 2, but entity '{}' is not"
                " dual circuit connectable".format(type(entity_1).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )
        if side2 == 2 and not entity_2.dual_circuit_connectable:
            warnings.warn(
                "'side2' was specified as 2, but entity '{}' is not"
                " dual circuit connectable".format(type(entity_2).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(
            entity_1.circuit_wire_max_distance, entity_2.circuit_wire_max_distance
        )
        entity_1_pos = [entity_1.position["x"], entity_1.position["y"]]
        entity_2_pos = [entity_2.position["x"], entity_2.position["y"]]
        real_dist = utils.dist(entity_1_pos, entity_2_pos)
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entities ({}) is greater than max connection distance"
                " ({})".format(real_dist, min_dist),
                ConnectionDistanceWarning,
                stacklevel=2,
            )

        # Add entity_2 to entity_1.connections

        if six.text_type(side1) not in entity_1.connections:
            entity_1.connections[six.text_type(side1)] = dict()
        current_side = entity_1.connections[six.text_type(side1)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # If dual circuit connectable specify the target side
        if entity_2.dual_circuit_connectable:
            entry = {"entity_id": entity_2, "circuit_id": side2}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": entity_2}

        if entry not in current_color:
            current_color.append(entry)

        # Add entity_1 to entity_2.connections

        if six.text_type(side2) not in entity_2.connections:
            entity_2.connections[six.text_type(side2)] = dict()
        current_side = entity_2.connections[six.text_type(side2)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # If dual circuit connectable specify the target side
        if entity_1.dual_circuit_connectable:
            entry = {"entity_id": entity_1, "circuit_id": side1}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": entity_1}

        if entry not in current_color:
            current_color.append(entry)

    def remove_circuit_connection(self, color, id1, id2, side1=1, side2=1):
        # type: (str, str, str, int, int) -> None
        """
        Removes a circuit wire connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side1 not in {1, 2}:
            raise InvalidConnectionSideError(side1)
        if side2 not in {1, 2}:
            raise InvalidConnectionSideError(side2)

        # Remove from source
        if entity_2.dual_circuit_connectable:
            entry = {"entity_id": entity_2, "circuit_id": side2}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": entity_2}

        try:
            current_side = entity_1.connections[six.text_type(side1)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from source if applicable
            if len(current_color) == 0:
                del entity_1.connections[six.text_type(side1)][color]
            if len(current_side) == 0:
                del entity_1.connections[six.text_type(side1)]
        except (KeyError, ValueError):
            pass

        # Remove from target
        if entity_1.dual_circuit_connectable:
            entry = {"entity_id": entity_1, "circuit_id": side1}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": entity_1}

        try:
            current_side = entity_2.connections[six.text_type(side2)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from target if applicable
            if len(current_color) == 0:
                del entity_2.connections[six.text_type(side2)][color]
            if len(current_side) == 0:
                del entity_2.connections[six.text_type(side2)]
        except (KeyError, ValueError):
            pass

    def remove_circuit_connections(self):
        # type: () -> None
        """
        Remove all power connections in the Collection.
        TODO: handle power switches
        """
        for entity in self.entities:
            if hasattr(entity, "connections"):
                entity.connections = None


# =============================================================================


@six.add_metaclass(abc.ABCMeta)
class TileCollection(object):
    """
    Abstract class used for other constructs that can contain EntityLikes, such
    as Blueprint.
    """

    @abc.abstractproperty
    def tiles(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def tile_hashmap(self):  # pragma: no coverage
        pass

    # =========================================================================
    # Queries
    # =========================================================================

    def find_tile(self, x, y):
        # type: (int, int) -> Tile
        """ """
        tiles = self.tile_hashmap.get_on_point((x + 0.5, y + 0.5))
        try:
            return tiles[0]
        except IndexError:
            return None

    def find_tiles_filtered(self, **kwargs):
        # type: (**dict) -> list[Tile]
        """
        Returns a filtered list of tiles within the blueprint. Works
        similarly to `LuaSurface.find_tiles_filtered`.

        Possible keywords include:
        * area: AABB to search in
        * position: grid position to search
        * radius: radius around position to search in
        * name: name or set of names, only entities with those names will be
        returned
        * limit: maximum number of entities to return
        """

        if "position" in kwargs and "radius" in kwargs:
            # Intersect entities with circle
            search_region = self.tile_hashmap.get_in_radius(
                kwargs["radius"], kwargs["position"]
            )
        elif "area" in kwargs:
            # Intersect entities with area
            search_region = self.tile_hashmap.get_in_area(kwargs["area"])
        else:
            search_region = self.tiles

        if isinstance(kwargs.get("name", None), str):
            names = {kwargs.pop("name", None)}
        else:
            names = kwargs.pop("name", None)

        # Keep track of how many
        limit = kwargs.pop("limit", len(search_region))

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            return True

        if kwargs.get("invert", False):
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]
