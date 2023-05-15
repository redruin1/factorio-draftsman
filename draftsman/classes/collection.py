# collection.py
# -*- encoding: utf-8 -*-

from draftsman.classes.association import Association
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.tile_list import TileList
from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.classes.schedule import Schedule
from draftsman.classes.spatial_data_structure import SpatialDataStructure
from draftsman.classes.tile import Tile
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, Orientation
from draftsman.error import (
    DraftsmanError,
    EntityNotPowerConnectableError,
    InvalidWireTypeError,
    InvalidConnectionSideError,
    InvalidAssociationError,
    EntityNotCircuitConnectableError,
)
from draftsman.warning import (
    ConnectionSideWarning,
    ConnectionDistanceWarning,
    TooManyConnectionsWarning,
)
from draftsman.utils import AABB, PrimitiveAABB, flatten_entities, distance

import abc
import six
from typing import Union
import warnings


@six.add_metaclass(abc.ABCMeta)
class EntityCollection(object):
    """
    Abstract class used to describe an object that can contain a list of
    :py:class:`~draftsman.classes.entitylike.EntityLike` instances.
    """

    # =========================================================================
    # Properties
    # =========================================================================

    @abc.abstractproperty
    def entities(self):  # pragma: no coverage
        # type: () -> EntityList
        """
        Object that holds the ``EntityLikes``, usually a :py:class:`.EntityList`.
        """
        pass

    @abc.abstractproperty
    def entity_map(self):  # pragma: no coverage
        # type: () -> SpatialDataStructure
        """
        Object that holds references to the entities organized by their spatial
        position. An implementation of :py:class:`.SpatialDataStructure`.
        """
        pass

    @property
    def rotatable(self):
        # type: () -> bool
        """
        Whether or not this collection can be rotated or not. Included for
        posterity; always returns True, even when containing entities that have
        no direction component. Read only.

        :type: ``bool``
        """
        return True

    @property
    def flippable(self):
        # type: () -> bool
        """
        Whether or not this collection can be flipped or not. This is determined
        by whether or not any of the entities contained can be flipped or not.
        Read only.

        :type: ``bool``
        """
        for entity in self.entities:
            if not entity.flippable:
                return False

        return True

    # =========================================================================
    # Custom edge functions for EntityList interaction
    # =========================================================================

    def on_entity_insert(self, entitylike, merge):  # pragma: no coverage
        # type: (EntityLike, bool) -> EntityLike
        """
        Function called when an :py:class:`.EntityLike` is inserted into this
        object's :py:attr:`entities` list (assuming that the ``entities`` list
        is a :py:class:`.EntityList`). By default, this function does nothing,
        but any child class can customize it's functionality by overriding it.
        """
        pass

    def on_entity_set(self, old_entitylike, new_entitylike):  # pragma: no coverage
        # type: (EntityLike, EntityLike) -> None
        """
        Function called when an :py:class:`.EntityLike` is replaced with another
        in this object's :py:attr:`entities` list (assuming that the ``entities``
        list is a :py:class:`.EntityList`). By default, this function does
        nothing, but any child class can customize it's functionality by
        overriding it.
        """
        pass

    def on_entity_remove(self, entitylike):  # pragma: no coverage
        # type: (EntityLike) -> None
        """
        Function called when an :py:class:`.EntityLike` is removed from this
        object's :py:attr:`entities` list (assuming that the ``entities`` list
        is a :py:class:`.EntityList`). By default, this function does nothing,
        but any child class can customize it's functionality by overriding it.
        """
        pass

    # =========================================================================
    # Entity Queries
    # =========================================================================

    def find_entity(self, name, position):
        # type: (str, Union[Vector, PrimitiveVector]) -> EntityLike
        """
        Finds an entity with ``name`` at a position ``position``. If multiple
        entities exist at the queried position, the one that was first placed is
        returned.

        :param name: The name of the entity to look for.
        :param position: The position to search, either a PrimitiveVector or a
            :py:class:`.Vector`.

        :retuns: The ``EntityLike`` at ``position``, or ``None`` of none were
            found.
        """
        results = self.entity_map.get_on_point(position)
        try:
            return list(filter(lambda x: x.name == name, results))[0]
        except IndexError:
            return None

    def find_entity_at_position(self, position):
        # type: (Union[Vector, PrimitiveVector]) -> EntityLike
        """
        Finds any entity at the position ``position``. If multiple entities
        exist at the queried position, the one that was first placed is returned.

        :param position: The position to search, either a PrimitiveVector or a
            :py:class:`.Vector`.

        :retuns: The ``EntityLike`` at ``position``, or ``None`` of none were
            found.
        """
        try:
            return self.entity_map.get_on_point(position)[0]
        except IndexError:
            return None

    def find_entities(self, aabb=None):
        # type: (Union[AABB, PrimitiveAABB]) -> list[EntityLike]
        """
        Returns a ``list`` of all entities within the area ``aabb``. Works
        similiarly to
        `LuaSurface.find_entities <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities>`_.
        If no ``aabb`` is provided then the method simply returns all the
        entities in the blueprint.

        :param aabb: An :py:class:`.AABB`, or a ``Sequence`` of 4 floats,
            usually a ``list`` or ``tuple``.

        :returns: A regular ``list`` of ``EntityLikes`` whose ``collision_box``
            overlaps the queried AABB.
        """
        if aabb is None:
            return list(self.entities)

        # Normalize AABB
        aabb = AABB.from_other(aabb)

        return self.entity_map.get_in_area(aabb)

    def find_entities_filtered(self, position=None, radius=None, area=None, name=None, type=None, direction=None, invert=False, limit=None):
        # type: (Vector, float, AABB, Union[str, set[str]], Union[str, set[str]], Union[Direction, set[Direction]], bool, int) -> list[EntityLike]
        """
        Returns a filtered list of entities within the ``Collection``. Works
        similarly to `LuaSurface.find_entities_filtered
        <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities_filtered>`_.

        Keywords are organized into two main categrories: **region** and
        **criteria**:

        .. list-table:: Region keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``position``
              - ``Vector`` or ``PrimitiveVector``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``AABB`` or ``PrimitiveAABB``
              - AABB to search in.

        If none of the above are specified, then the search area becomes the 
        entire Collection. If ``radius`` is specified but ``position`` is not,
        the search area also becomes the entire Collection.

        .. list-table:: Criteria keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``name``
              - ``str`` or ``set{str}``
              - The name(s) of the entities that you want to search for.
            * - ``type``
              - ``str`` or ``set{str}``
              - The type(s) of the entities that you want to search for.
            * - ``direction``
              - ``Direction`` or ``set{Direction}``
              - | The direction(s) of the entities that you want to search for.
                | Excludes entities that have no direction.
            * - ``limit``
              - ``int``
              - | Limit the maximum size of the returned list to this amount.
                | Unlimited by default.
            * - ``invert``
              - ``bool``
              - | Whether or not to return the inverse of the search.
                | False by default.

        :param position: The global position to search the source Collection.
            Can be used in conjunction with ``radius`` to search a circle 
            instead of a single point. Takes precedence over ``area``.
        :param radius: The radius of the circle centered around ``position`` to
            search. Must be defined alongside ``position`` in order to search in
            a circular area.
        :param aabb: The :py:class:`AABB` or (``PrimitiveAABB``) to search in.
        :param name: Either a ``str``, or a ``set[str]`` where each entry is a 
            name of an entity to be returned.
        :param type: Either a ``str``, or a ``set[str]`` where each entry is a 
            type of an entity to be returned.
        :param direction: Either a :py:class:`Direction` enum (or corresponding
            ``int``), or a ``set[Direction]`` where each entry is a valid
            direction for each returned entity to match. Excludes entities that 
            have no direction attribute.
        :param invert: Whether or not to return the inversion of the search
            criteria.
        :param limit: The total number of matching entities to return. Unlimited
            by default.

        :returns: A list of entity references inside the searched collection 
            that satisfy the search criteria.
        """

        if position is not None:
            if radius is not None:
                # Intersect entities with circle
                search_region = self.entity_map.get_in_radius(
                    radius, position
                )
            else:
                # Intersect entities with point
                search_region = self.entity_map.get_on_point(position)
        elif area is not None:
            # Intersect entities with area
            area = AABB.from_other(area)
            search_region = self.entity_map.get_in_area(area)
        else:
            # Search all entities, but make sure it's a 1D list
            search_region = flatten_entities(self.entities)

        # Normalize inputs
        if isinstance(name, str):
            names = {name}
        else:
            names = name
        if isinstance(type, str):
            types = {type}
        else:
            types = type
        if isinstance(direction, int):
            directions = {direction}
        else:
            directions = direction

        # Keep track of how many
        if limit is None:
            limit = len(search_region)

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

        if invert:
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]

    # =========================================================================
    # Connections
    # =========================================================================

    def add_power_connection(self, entity_1, entity_2, side=1):
        # type: (Union[EntityLike, int, str], Union[EntityLike, int, str], int) -> None
        """
        Adds a copper wire power connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. Tuples of
        strings and ints mean to recursively search through
        :py:class:`EntityCollection` instances in the base level, following the
        logic of :py:meth:`.EntityList.__getitem__`. For example:

        .. code-block:: python

            blueprint.entities.append("small-electric-pole")
            group = Group("group") # Type of EntityCollection
            group.entities.append("small-electric-pole", tile_position=(5, 0))
            blueprint.entities.append(group)

            # Add a connection between the first power pole and the first entity
            # in the group
            blueprint.add_power_connection(blueprint.entities[0], ("group", 0))

        Side specifies which side to connect to when establishing a
        connection to a dual-power-connectable entity (usually a power-switch).
        Does nothing if the connection already exists.

        Raises :py:class:`~draftsman.warning.ConnectionRangeWarning` if the
        distance between the two entities exceeds the maximum wire distance
        between the two.

        Raises :py:class:`~draftsman.warning.TooManyConnectionsWarning` if
        either of the power poles exceed 5 connections when this connection is
        added.

        .. NOTE::

            ``side`` is in 1-based notation (1 and 2, input and output) which is
            identical to circuit connections. Internally, however, the
            connections are represented in 0-based notation as "Cu0" and "Cu1"
            respectively.

        .. NOTE::

            You might notice that unlike :py:meth:`add_circuit_connection`,
            there is only one ``side`` argument. This is because it is actually
            impossible to connect two dual-power-connectable entities with one
            another; they must be connected to a power pole in-between.

        :param entity_1: EntityLike, ID, or index of the first entity to join.
        :param entity_2: EntityLike, ID or index of the second entity to join.
        :param side: Which side of a dual-power-connectable entity to connect
            to, where ``1`` is "input" and ``2`` is "output". Only used when
            connecting a dual-power-connectable entity. Defaults to ``1``.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        :exception InvalidConnectionSideError: If ``side`` is neither ``1`` nor
            ``2``.
        :exception EntityNotPowerConnectableError: If either `entity_1` or
            `entity_2` do not have the capability to be copper wire connected.
        :exception DraftsmanError: If both `entity_1` and `entity_2` are
            dual-power-connectable, of which a connection is forbidden.
        """
        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        if side not in {1, 2}:
            raise InvalidConnectionSideError("'{}'".format(side))

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
        real_dist = distance(
            entity_1.global_position._data, entity_2.global_position._data
        )
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entity '{}' and entity '{}' ({}) is greater"
                " than max connection distance ({})".format(
                    entity_1.name, entity_2.name, real_dist, min_dist
                ),
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

        # Only worried about entity_1
        if entity_1.dual_power_connectable:  # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in entity_1.connections:
                entity_1.connections[str_side] = []

            entry = {"entity_id": Association(entity_2), "wire_id": 0}
            if entry not in entity_1.connections[str_side]:
                entity_1.connections[str_side].append(entry)
        else:  # electric pole
            if not entity_2.dual_power_connectable:
                if Association(entity_2) not in entity_1.neighbours:
                    entity_1.neighbours.append(Association(entity_2))

        # Only worried about entity_2
        if entity_2.dual_power_connectable:  # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in entity_2.connections:
                entity_2.connections[str_side] = []

            entry = {"entity_id": Association(entity_1), "wire_id": 0}
            if entry not in entity_2.connections[str_side]:
                entity_2.connections[str_side].append(entry)
        else:  # electric pole
            if not entity_1.dual_power_connectable:
                if Association(entity_1) not in entity_2.neighbours:
                    entity_2.neighbours.append(Association(entity_1))

    def remove_power_connection(self, entity_1, entity_2, side=1):
        # type: (Union[EntityLike, int, str], Union[EntityLike, int, str], int) -> None
        """
        Removes a copper wire power connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. ``side``
        specifies which side to remove the connection from when removing a
        connection to a dual-power-connectable entity (usually a power-switch).
        Does nothing if the specified connection does not exist.

        :param entity_1: EntityLike, ID or index of the first entity to remove
            the connection to.
        :param entity_2: EntityLike, ID or index of the second entity to remove
            the connection to.
        :param side: Which side of a dual-power-connectable entity to remove the
            connection from, where ``1`` is "input" and ``2`` is "output". Only
            used when disjoining a dual-power-connectable entity. Defaults to
            ``1``.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        """
        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        # Only worried about self
        if entity_1.dual_power_connectable:  # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": Association(entity_2), "wire_id": 0}
            if str_side in entity_1.connections:
                if entry in entity_1.connections[str_side]:
                    entity_1.connections[str_side].remove(entry)
                if len(entity_1.connections[str_side]) == 0:
                    del entity_1.connections[str_side]
        else:  # electric pole
            if not entity_2.dual_power_connectable:
                try:
                    entity_1.neighbours.remove(Association(entity_2))
                except ValueError:
                    pass

        # Only worried about target
        if entity_2.dual_power_connectable:  # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": Association(entity_1), "wire_id": 0}
            if str_side in entity_2.connections:
                if entry in entity_2.connections[str_side]:
                    entity_2.connections[str_side].remove(entry)
                if len(entity_2.connections[str_side]) == 0:
                    del entity_2.connections[str_side]
        else:  # electric pole
            if not entity_1.dual_power_connectable:
                try:
                    entity_2.neighbours.remove(Association(entity_1))
                except ValueError:
                    pass

    def remove_power_connections(self):
        # type: () -> None
        """
        Remove all power connections in the Collection, including any power
        connections between power switches. Recurses through any subgroups, and
        removes power connections from them as well. Does nothing if there are
        no power connections in the Collection.
        """
        for entity in self.entities:
            if isinstance(entity, EntityCollection):
                # Recursively remove connections from subgroups
                entity.remove_power_connections()
            else:
                # Remove the connections for this particular entity
                if hasattr(entity, "neighbours"):
                    entity.neighbours = None
                if hasattr(entity, "connections"):
                    if "Cu0" in entity.connections:
                        del entity.connections["Cu0"]
                    if "Cu1" in entity.connections:
                        del entity.connections["Cu1"]

    def generate_power_connections(self, prefer_axis=True, only_axis=False):
        # type: (bool, bool) -> None
        """
        Automatically create power connections between all electric poles.

        The algorithm used is similar to demi-pixel's `generateElectricalConnections()
        <https://github.com/demipixel/factorio-blueprint/blob/master/src/electrical-connections.ts>`_
        function, but with some slight differences. Power poles are still
        prioritized closest first, but can be selected to prefer to connect
        neighbours on the same axis, as well as *only* connect to neighbours on
        the same axis. This function will only connect power poles that have
        less than 5 power connections already made, preserving power connections
        that were manually specified. This function does not generate
        connections between power-switches.

        :param prefer_axis: Determines whether or not to rank power-poles on the
            same x or y coordinate higher than poles that are closer, but not on
            either axis. Used to prefer creating neat, regular grids when
            possible.
        :param only_axis: Removes any neighbour that does not lie on the same
            x or y axis from the candidate pool, preventing non-grid
            connections.
        """
        # Get all power poles in the Collection (1D list)
        electric_poles = self.find_entities_filtered(type="electric-pole")
        for cur_pole in electric_poles:
            # Get all the power poles candidates
            def power_connectable(other):
                # type: (EntityLike) -> bool
                # Don't include ourself in the entities we're connecting to
                if other is cur_pole:
                    return False
                # If only_axis is true, only include ones that have the same x
                # or y
                if (
                    cur_pole.global_position.x != other.global_position.x
                    and cur_pole.global_position.y != other.global_position.y
                    and only_axis
                ):
                    return False
                # Only return poles that are less than the max power pole
                # distance
                dist = distance(
                    cur_pole.global_position._data, other.global_position._data
                )
                min_dist = min(
                    cur_pole.maximum_wire_distance, other.maximum_wire_distance
                )
                return dist <= min_dist

            potential_neighbours = list(filter(power_connectable, electric_poles))
            # Sort the power poles by distance
            potential_neighbours.sort(
                key=lambda x: distance(
                    x.global_position._data, cur_pole.global_position._data
                )
            )

            # Sort the power poles by whether or not they are on the axis first
            if prefer_axis:
                potential_neighbours.sort(
                    key=lambda x: not (
                        x.global_position.x == cur_pole.global_position.x
                        or x.global_position.y == cur_pole.global_position.y
                    )
                )

            # Iterate over every potential neighbour
            while len(potential_neighbours) > 0:
                neighbour = potential_neighbours.pop()
                # Make sure this connection would not exceed each entities max
                # connections
                if len(cur_pole.neighbours) < 5 and len(neighbour.neighbours) < 5:
                    self.add_power_connection(cur_pole, neighbour)

    # =========================================================================

    def add_circuit_connection(self, color, entity_1, entity_2, side1=1, side2=1):
        # type: (str, Union[EntityLike, int, str], Union[EntityLike, int, str], int, int) -> None
        """
        Adds a circuit wire connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. Color
        specifies the color of the wire to make the connection with, and is
        either ``"red"`` or ``"green"``. ``side1`` specifies which side of the
        first entity to connect to (if applicable), and ``side2`` specifies
        which side of the second entity to connect to (if applicable). Does
        nothing if the connection already exists.

        Raises :py:class:`~draftsman.warning.ConnectionSideWarning` if the side
        of either of the entities is ``2`` when the entity is not
        dual-circuit-connectable.

        Raises :py:class:`~draftsman.warning.ConnectionRangeWarning` if the
        distance between the two entities exceeds the maximum wire distance
        between the two.

        :param color: Color of the wire to make the connection with. Must be
            either ``"red"`` or ``"green"``.
        :param id1: ID or index of the first entity to join.
        :param id2: ID or index of the second entity to join.
        :param side1: Which side of the first dual-circuit-entity to connect to,
            where ``1`` is "input" and ``2`` is "output". Only used when the
            first entity is dual-circuit-connectable. Defaults to ``1``.
        :param side2: Which side of the second dual-circuit-entity to connect
            to, where ``1`` is "input" and ``2`` is "output". Only used when the
            second entity is dual-circuit-connectable. Defaults to ``1``.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are invalid
            ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        :exception InvalidWireTypeError: If ``color`` is neither ``"red"`` nor
            ``"green"``.
        :exception InvalidConnectionSideError: If ``side1`` or ``side2`` are
            neither ``1`` nor ``2``.
        :exception EntityNotCircuitConnectableError: If either `entity_1` or
            `entity_2` do not have the capability to be circuit wire connected.
        """
        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side1 not in {1, 2}:
            raise InvalidConnectionSideError("'{}'".format(side1))
        if side2 not in {1, 2}:
            raise InvalidConnectionSideError("'{}'".format(side2))

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
        real_dist = distance(
            entity_1.global_position._data, entity_2.global_position._data
        )
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entity '{}' and entity '{}' ({}) is greater"
                " than max connection distance ({})".format(
                    entity_1.name, entity_2.name, real_dist, min_dist
                ),
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
            entry = {"entity_id": Association(entity_2), "circuit_id": side2}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": Association(entity_2)}

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
            entry = {"entity_id": Association(entity_1), "circuit_id": side1}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": Association(entity_1)}

        if entry not in current_color:
            current_color.append(entry)

    def remove_circuit_connection(self, color, entity_1, entity_2, side1=1, side2=1):
        # type: (str, Union[EntityLike, int, str], Union[EntityLike, int, str], int, int) -> None
        """
        Removes a circuit wire connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. ``side1``
        specifies which side of the first entity to remove the connection from
        (if applicable), and ``side2`` specifies which side of the second entity
        to remove the connection from (if applicable). Does nothing if the
        specified connection doesn't exist.

        :param color: Color of the wire to remove. Either ``"red"`` or
            ``"green"``.
        :param entity_1: ID or index of the first entity to remove the
            connection to.
        :param entity_@: ID or index of the second entity to remove the
            connection to.
        :param side1: Which side of the first dual-circuit-connectable entity to
            remove the connection from, where ``1`` is "input" and ``2`` is
            "output". Only used when disjoining a dual-circuit-connectable
            entity. Defaults to ``1``.
        :param side2: Which side of the second dual-circuit-connectable entity
            to remove the connection from, where ``1`` is "input" and ``2`` is
            "output". Only used when disjoining a dual-circuit-connectable
            entity. Defaults to ``1``.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        """
        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side1 not in {1, 2}:
            raise InvalidConnectionSideError(side1)
        if side2 not in {1, 2}:
            raise InvalidConnectionSideError(side2)

        # Remove from source
        if entity_2.dual_circuit_connectable:
            entry = {"entity_id": Association(entity_2), "circuit_id": side2}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": Association(entity_2)}

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
            entry = {"entity_id": Association(entity_1), "circuit_id": side1}
        else:
            # However, for most entities you dont need a target side
            entry = {"entity_id": Association(entity_1)}

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
        Remove all circuit connections in the Collection. Recurses through all
        subgroups and removes circuit connections from them as well. Does
        nothing if there are no circuit connections in the Collection.
        """
        for entity in self.entities:
            if isinstance(entity, EntityCollection):
                # Recursively remove connections from subgroups
                entity.remove_circuit_connections()
            else:
                # Remove the connections from this particular entity
                if hasattr(entity, "connections"):
                    if "1" in entity.connections:
                        del entity.connections["1"]
                    if "2" in entity.connections:
                        del entity.connections["2"]

    # =========================================================================
    # Trains
    # =========================================================================

    def add_train_at_position(self, config, position, direction, schedule=None):
        # type: (TrainConfiguration, Vector, Direction, Schedule) -> None
        """
        Adds a train with a specified configuration and schedule at a position
        facing a particular direction. Allows you to place a fully configured
        train in a single function call.

        .. NOTE:

            Currently can only place trains in a straight line; horizontally,
            vertically, or diagonally. Does not obey curved rails.

        .. see-also:

            :py:meth:`add_train_at_station`

        :param config: The :py:class:`TrainConfiguration` to use as a template 
            for the created train.
        :param position: A :py:class:`Vector` specifying the center of the 
            starting wagon.
        :param direction: A :py:class:`Direction` enum or ``int`` specifying
            which direction the train is "facing".
        :param schedule: A :py:class:`Schedule` object specifying the schedule
            that the newly created train should inherit.
        """
        current_pos = Vector.from_other(position)
        for entity in config.cars:
            orientation = (direction.to_orientation() + entity.orientation) % 1.0
            self.entities.append(
                entity, copy=True, position=current_pos, orientation=orientation
            )
            current_pos += direction.to_vector(-7) # 7 = distance between wagons

        # TODO: schedule
        

    def add_train_at_station(self, config, station, schedule=None):
        # type: (TrainConfiguration, Union[EntityLike, str, int], Schedule, bool) -> None
        """
        Adds a train with a specified configuration and schedule behind a 
        specified train stop.

        .. NOTE:

            Currently can only place trains in a straight line; horizontally or
            vertically. Does not obey curved rails.

        .. see-also:

            :py:meth:`add_train_at_position`

        :param config: The :py:class:`TrainConfiguration` to use as a template 
            for the created train.
        :param station: The ID or index of the train entity stop to spawn behind.
        :param schedule: A :py:class:`Schedule` object specifying the schedule
            that the newly created train should inherit.
        """
        if not isinstance(station, EntityLike):
            station = self.entities[station]

        # TODO: ensure that the specified station is actually a station
        # if not isinstance(station, TrainStop):
        #     raise ValueError("bruh moment")

        shift_over = station.direction.previous().to_vector(3)
        shift_back = station.direction.to_vector(4)
        current_pos = station.tile_position - shift_back + shift_over
        for entity in config.cars:
            orientation = station.direction.to_orientation() + entity.orientation
            self.entities.append(
                entity, copy=True, position=current_pos, orientation=orientation 
            )
            current_pos += station.direction.to_vector(-7) # 7 = distance between wagons

        # TODO: schedule

    # =========================================================================
    # Train Queries
    # =========================================================================

    def find_trains_filtered(self, train_length=None, num_type=None, orientation=None, config=None, invert=False, limit=None):
        # type: (int, dict, Orientation, TrainConfiguration, bool, int) -> list[list[EntityLike]]
        """
        Finds a set of trains that match the passed in parameters. Formally, a 
        "train" is a connected set of wagons consisting of at least one 
        locomotive. Since blueprint strings contain no information regarding
        train-connectivity, train connections are inferred from their relative
        ``position`` and ``orientation``.

        .. NOTE:

            When using the ``config`` parameter, equality is strictly checked;
            which means that if a returned train doesn't _exactly_ match the 
            specified argument, the train is filtered from the result. This 
            includes things like item fuel requests and cargo wagon item filters, 
            so check these values in the blueprints you're searching and adjust
            ``config`` accordingly.

        :param train_length: Can either be specified as an ``int`` representing
            the maximum length of trains to return (inclusive), or as a 
            ``Sequence`` of 2 ``int``s representing the minimum and maximum 
            length of trains to return (inclusive).
        :param num_type: A ``dict`` of wagon types where each key is the ``str``
            type of the wagon and the value is an ``int`` representing the
            desired number of those wagons in the returned train. Allows to
            search for trains of a particular composition without regards to
            contents, order, or orientation.
        :param orientation: A :py:class:`Orientation` (or equivalent ``float``)
            that describes the orientation that every car in the returned train
            list should have. Note that trains placed on curved rails will not
            be returned by this parameter, as _all_ train cars must equal 
            ``orientation``.
        :param config: A :py:class:`TrainConfiguration` object to filter against.
            Performs a strict equality check between each of the train 
            configuration's cars and the cars in the returned trains.
        :param invert: Whether or not to return the inversion of the search
            criteria.
        :param limit: A maximum number of unique trains to return. 

        :returns: A ``list`` of ``list``s, where each sub-list represents a 
            contiguous train. Trains are ordered such that the first index is 
            the "front" of the train as chosen by the orientation of the first
            found locomotive in that group. In cases where a train has 
            locomotives in both directions, an arbitrary direction is selected.
        """
        locomotives = self.find_entities_filtered(type={"locomotive"})
        trains = []
        used_wagons = set() # Create a set of trains to check 

        def traverse_neighbours(wagon, current_train, wagon_direction=1):
            neighbours = self.find_entities_filtered(
                position=wagon.position, 
                radius=7.5, # Average distance is less than 7 tiles
                type={"locomotive", "cargo-wagon", "fluid-wagon", "artillery-wagon"}
            )
            for neighbour in neighbours:
                # Check to make sure we haven't already added this wagon to a
                # train
                if neighbour in used_wagons:
                    continue

                # Check the orientation
                # If the orientation is +- 45 degrees in either direction:
                if neighbour.orientation.in_range(
                    wagon.orientation - 0.125,
                    wagon.orientation + 0.125
                ) or neighbour.orientation.in_range(
                    wagon.orientation.opposite() - 0.125,
                    wagon.orientation.opposite() + 0.125
                ):
                    # Determine the neighbour closest truck point
                    a = neighbour.position + neighbour.orientation.to_vector(2)
                    b = neighbour.position + neighbour.orientation.to_vector(-2)
                    if distance(wagon.position, a) < distance(wagon.position, b):
                        neighbour_truck = a
                        direction = 1
                    else:
                        neighbour_truck = b
                        direction = -1

                    # Check front
                    wagon_truck = wagon.position + wagon.orientation.to_vector(2) 
                    if 2.9 < distance(wagon_truck, neighbour_truck) <= 3.1:
                        # Add to beginning of train list
                        used_wagons.add(neighbour)
                        current_train.insert(0, neighbour)
                        traverse_neighbours(neighbour, current_train, direction)

                    # Check back
                    wagon_truck = wagon.position + wagon.orientation.to_vector(-2)
                    if 2.9 < distance(wagon_truck, neighbour_truck) <= 3.1:
                        # Add to end of train list
                        used_wagons.add(neighbour)
                        current_train.append(neighbour)
                        traverse_neighbours(neighbour, current_train)

            return current_train

        # Get all contiguous trains
        # TODO: this could probably be more performant if we check train 
        # validity as we iterate, meaning we could simply early exit if we 
        # exceed `limit` for example
        for locomotive in locomotives:
            if locomotive in used_wagons:
                continue
            used_wagons.add(locomotive)
            train = traverse_neighbours(locomotive, [locomotive])
            trains.append(train)

        # Normalize inputs
        if isinstance(train_length, int):
            train_length = [0, train_length]
        if limit is None:
            limit = len(trains)

        # Filter based on parameters
        def test(train):
            if train_length is not None:
                if len(train) < train_length[0] or len(train) > train_length[1]:
                    return False
            if num_type is not None:
                for desired_type, desired_count in num_type.items():
                    num_train_type = sum(x.type == desired_type for x in train)
                    if num_train_type != desired_count:
                        return False
            if orientation is not None:
                for train_car in train:
                    if train_car.orientation != orientation:
                        return False
            if config is not None:
                if len(train) != len(config.cars):
                    return False
                for i, config_car in enumerate(config.car):
                    if train[i] != config_car:
                        return False
            return True

        if invert:
            return list(filter(lambda train: not test(train), trains))[:limit]
        else:
            return list(filter(lambda train: test(train), trains))[:limit]


# =============================================================================


@six.add_metaclass(abc.ABCMeta)
class TileCollection(object):
    """
    Abstract class used to describe an object that can contain a list of
    :py:class:`.Tile` instances.
    """

    @abc.abstractproperty
    def tiles(self):  # pragma: no coverage
        # type: () -> TileList
        """
        Object that holds the ``Tiles``, usually a
        :py:class:`~draftsman.classes.tilelist.TileList`.
        """
        pass

    @abc.abstractproperty
    def tile_map(self):  # pragma: no coverage
        # type: () -> SpatialDataStructure
        """
        Object that holds the spatial information for the Tiles of this object,
        usually a :py:class:`~draftsman.classes.spatialhashmap.SpatialHashMap`.
        """
        pass

    # =========================================================================
    # Custom edge functions for TileList interaction
    # =========================================================================

    def on_tile_insert(self, tile, merge):  # pragma: no coverage
        # type: (Tile, bool) -> Tile
        """
        Function called when an :py:class:`.Tile` is inserted into this object's
        :py:attr:`tiles` list (assuming that the ``tiles`` list is a
        :py:class:`.TileList`). By default, this function does nothing, but any
        child class can customize it's functionality by overriding it.
        """
        pass

    def on_tile_set(self, old_tile, new_tile):  # pragma: no coverage
        # type: (Tile, bool) -> None
        """
        Function called when an :py:class:`.Tile` is replaced with another in
        this object's :py:attr:`tiles` list (assuming that the ``tiles`` list is
        a :py:class:`.TileList`). By default, this function does nothing, but
        any child class can customize it's functionality by overriding it.
        """
        pass

    def on_tile_remove(self, tile):  # pragma: no coverage
        # type: (Tile) -> None
        """
        Function called when an :py:class:`.Tile` is removed from this object's
        :py:attr:`tiles` list (assuming that the ``entities`` list is a
        :py:class:`.TileList`). By default, this function does nothing, but any
        child class can customize it's functionality by overriding it.
        """
        pass

    # =========================================================================
    # Queries
    # =========================================================================

    def find_tile(self, position):
        # type: (Union[Vector, PrimitiveVector]) -> Tile
        """
        Returns the tile at the tile coordinate ``position``. If there are
        multiple tiles at that location, the entity that was inserted first is
        returned.

        :param position: The position to search, either a PrimitiveVector or a
            :py:class:`.Vector`.

        :returns: The tile at ``position``, or ``None`` if there is none.
        """
        tiles = self.tile_map.get_on_point(Vector(0.5, 0.5) + position)
        try:
            return tiles[0]
        except IndexError:
            return None

    def find_tiles_filtered(self, **kwargs):
        # type: (**dict) -> list[Tile]
        """
        Returns a filtered list of tiles within the blueprint. Works
        similarly to
        `LuaSurface.find_tiles_filtered <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_tiles_filtered>`_.

        Keywords are organized into two main categrories: **region** and
        **criteria**:

        .. list-table:: Region keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``position``
              - ``Vector`` or ``PrimitiveVector``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``AABB`` or ``PrimitiveAABB``
              - AABB to search in.

        .. list-table:: Criteria keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``name``
              - ``str`` or ``set{str}``
              - The name(s) of the entities that you want to search for.
            * - ``limit``
              - ``int``
              - | Limit the maximum size of the returned list to this amount.
                | Unlimited by default.

        ``position`` and ``radius`` take precidence over ``aabb`` if all are
        specified. If no region keywords are specified, the entire Collection is
        searched.
        """

        if "position" in kwargs and "radius" in kwargs:
            # Intersect entities with circle
            search_region = self.tile_map.get_in_radius(
                kwargs["radius"], kwargs["position"]
            )
        elif "area" in kwargs:
            # Intersect entities with area
            area = AABB.from_other(kwargs["area"])
            search_region = self.tile_map.get_in_area(area)
        else:
            search_region = self.tiles

        if isinstance(kwargs.get("name", None), str):
            names = {kwargs.pop("name", None)}
        else:
            names = kwargs.pop("name", None)

        # Keep track of how many
        limit = kwargs.pop("limit", len(search_region))

        def test(tile):
            if names is not None and tile.name not in names:
                return False
            return True

        if kwargs.get("invert", False):
            return list(filter(lambda tile: not test(tile), search_region))[:limit]
        else:
            return list(filter(lambda tile: test(tile), search_region))[:limit]
