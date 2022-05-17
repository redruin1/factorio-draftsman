# collection.py
# -*- encoding: utf-8 -*-

from draftsman.classes.association import Association
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.spatialhashmap import SpatialHashMap
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
        Object that holds the ``EntityLikes``, usually a
        :py:class:`~draftsman.classes.entitylist.EntityList`.
        """
        pass

    @abc.abstractproperty
    def entity_hashmap(self):  # pragma: no coverage
        # type: () -> SpatialHashMap
        """
        Object that holds the spatial information of the entities of this object,
        usually a :py:class:`~draftsman.classes.spatialhashmap.SpatialHashMap`.
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

    def on_entity_insert(self, entitylike):  # pragma: no coverage
        # type: (EntityLike) -> None
        """
        Function called when an ``EntityLike`` is inserted into this object's
        ``entities`` list (assuming that the ``entities`` list is a
        ``EntityList``). By default, this function does nothing, but any
        child class can customize it's functionality by overriding it.
        """
        pass

    def on_entity_set(self, old_entitylike, new_entitylike):  # pragma: no coverage
        # type: (EntityLike, EntityLike) -> None
        """
        Function called when an ``EntityLike`` is replaced with another in this
        object's ``entities`` list (assuming that the ``entities`` list is a
        ``EntityList``). By default, this function does nothing, but any
        child class can customize it's functionality by overriding it.
        """
        pass

    def on_entity_remove(self, entitylike):  # pragma: no coverage
        # type: (EntityLike) -> None
        """
        Function called when an ``EntityLike`` is removed from this object's
        ``entities`` list (assuming that the ``entities`` list is a
        ``EntityList``). By default, this function does nothing, but any
        child class can customize it's functionality by overriding it.
        """
        pass

    # =========================================================================
    # Queries
    # =========================================================================

    def find_entity(self, name, position):
        # type: (str, Union[tuple, list, dict]) -> EntityLike
        """
        Finds an entity with ``name`` at a grid position ``position``. If
        multiple entities exist in the queried position, the one that was first
        placed is returned.

        :param name: The name of the entity to look for.
        :param position: Either a sequence of two ``floats``, or a ``dict`` with
            an ``"x"`` and ``"y"`` keys.

        :retuns: The ``EntityLike`` at ``position``, or ``None`` of none were
            found.
        """
        results = self.entity_hashmap.get_on_point(position)
        try:
            return list(filter(lambda x: x.name == name, results))[0]
        except IndexError:
            return None

    def find_entities(self, aabb=None):
        # type: (list) -> list[EntityLike]
        """
        Returns a list of all entities within the area ``aabb``. Works
        similiarly to
        `LuaSurface.find_entities <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities>`_.
        If no ``aabb`` is provided then the method simply returns all the
        entities in the blueprint.

        :param aabb: A list of two lists, each of two floats. The first pair
            represents the top-left corner (minimum) and the second the
            bottom-right corner (maximum).

        :returns: A regular ``list`` of ``EntityLikes`` whose ``collision_box``
            overlaps the queried AABB.
        """
        if aabb is None:
            return list(self.entities)

        return self.entity_hashmap.get_in_area(aabb)

    def find_entities_filtered(self, **kwargs):
        # type: (**dict) -> list[EntityLike]
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
              - ``[float, float]`` or ``{"x": float, "y": float}``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``[[float, float], [float, float]]``
              - AABB to search in.

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

        ``position`` and ``radius`` take precidence over ``aabb`` if all are
        specified. If no region keywords are specified, the entire Collection is
        searched.
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
            # Search all entities, but make sure it's a 1D list
            search_region = utils.flatten_entities(self.entities)

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
        # type: (Union[str, int], Union[str, int], int) -> None
        """
        Adds a copper wire power connection between two entities. Each ID can
        either be the index of the entity in the ``entities`` list, or it's
        string ID. Side specifies which side to connect to when establishing a
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

        :param id1: ID or index of the first entity to join.
        :param id2: ID or index of the second entity to join.
        :param side: Which side of a dual-power-connectable entity to connect
            to, where ``1`` is "input" and ``2`` is "output". Only used when
            connecting a dual-power-connectable entity. Defaults to ``1``.

        :exception KeyError, IndexError: If ``id1`` and/or ``id2`` are invalid
            ID's or indices to the parent Collection.
        :exception InvalidConnectionSideError: If ``side`` is neither ``1`` nor
            ``2``.
        :exception EntityNotPowerConnectableError: If either `entity1` or
            `entity2` do not have the capability to be copper wire connected.
        :exception DraftsmanError: If both `entity1` and `entity2` are
            dual-power-connectable, of which a connection is forbidden.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

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

            entry = {"entity_id": Association(entity_2), "wire_id": 0}
            if entry not in entity_1.connections[str_side]:
                entity_1.connections[str_side].append(entry)
        else:  # electric pole
            if not entity_2.dual_power_connectable:
                if Association(entity_2) not in entity_1.neighbours:
                    entity_1.neighbours.append(Association(entity_2))

        # Only worried about target
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

    def remove_power_connection(self, id1, id2, side=1):
        # type: (str, str, int) -> None
        """
        Removes a copper wire power connection between two entities. Each id can
        either be the index of the entity in the ``entities`` list, or it's
        string ID. ``side`` specifies which side to remove the connection from
        when removing a connection to a dual-power-connectable entity (usually a
        power-switch). Does nothing if the connection does not exist.

        :param id1: ID or index of the first entity to remove the connection to.
        :param id2: ID or index of the second entity to remove the connection
            to.
        :param side: Which side of a dual-power-connectable entity to remove the
            connection from, where ``1`` is "input" and ``2`` is "output". Only
            used when disjoining a dual-power-connectable entity. Defaults to
            ``1``.

        :exception KeyError, IndexError: If ``id1`` and/or ``id2`` are invalid
            ID's or indices to the parent Collection.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

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
        connections between power switches. Does nothing if there are no power
        connections in the Collection.
        """
        for entity in self.entities:
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
            possible. ``True`` by default.
        :param only_axis: Removes any neighbour that does not lie on the same
            x or y axis from the candidate pool, preventing non grid
            connections. ``False`` by default.
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
                # If only_axis is true, only include ones that have the same x
                # or y
                if (
                    cur_pole.position["x"] != other.position["x"]
                    and cur_pole.position["y"] != other.position["y"]
                    and only_axis
                ):
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
            potential_neighbours.sort(
                key=lambda x: utils.dist(x.position, cur_pole.position)
            )
            # potential_neighbours = sorted(
            #     potential_neighbours,
            #     key=lambda x: utils.dist(x.position, cur_pole.position),
            #     reverse=True,
            # )
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
        Adds a circuit wire connection between two entities. Each ID can
        either be the index of the entity in the ``entities`` list, or it's
        string ID. Color specifies the color of the wire to make the connection
        with, and is either ``"red"`` or ``"green"``. ``side1`` specifies which
        side of the first entity to connect to (if applicable), and ``side2``
        specifies which side of the second entity to connect to (if applicable).
        Does nothing if the connection already exists.

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

        :exception KeyError, IndexError: If ``id1`` and/or ``id2`` are invalid
            ID's or indices to the parent Collection.
        :exception InvalidWireTypeError: If ``color`` is neither ``"red"`` nor
            ``"green"``.
        :exception InvalidConnectionSideError: If ``side1`` or ``side2`` are
            neither ``1`` nor ``2``.
        :exception EntityNotCircuitConnectableError: If either `entity_1` or
            `entity_2` do not have the capability to be circuit wire connected.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

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
        entity_1_pos = [entity_1.global_position["x"], entity_1.global_position["y"]]
        entity_2_pos = [entity_2.global_position["x"], entity_2.global_position["y"]]
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

    def remove_circuit_connection(self, color, id1, id2, side1=1, side2=1):
        # type: (str, str, str, int, int) -> None
        """
        Removes a circuit wire connection between two entities. Each ID can
        either be the index of the entity in the ``entities`` list, or it's
        string ID. ``side1`` specifies which side of the first entity to remove
        the connection from (if applicable), and ``side2`` specifies which side
        of the second entity to remove the connection from (if applicable). Does
        nothing if the connection doesn't exist.

        :param color: Color of the wire to remove. Either ``"red"`` or
            ``"green"``.
        :param id1: ID or index of the first entity to remove the connection to.
        :param id2: ID or index of the second entity to remove the connection to.
        :param side1: Which side of the first dual-circuit-connectable entity to
            remove the connection from, where ``1`` is "input" and ``2`` is
            "output". Only used when disjoining a dual-circuit-connectable
            entity. Defaults to ``1``.
        :param side2: Which side of the second dual-circuit-connectable entity
            to remove the connection from, where ``1`` is "input" and ``2`` is
            "output". Only used when disjoining a dual-circuit-connectable
            entity. Defaults to ``1``.

        :exception KeyError, IndexError: If ``id1`` and/or ``id2`` are invalid
            ID's or indices to the parent Collection.
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
        Remove all circuit connections in the Collection. Does nothing if there
        are no circuit connections in the Collection
        """
        for entity in self.entities:
            if hasattr(entity, "connections"):
                if "1" in entity.connections:
                    del entity.connections["1"]
                if "2" in entity.connections:
                    del entity.connections["2"]


# =============================================================================


@six.add_metaclass(abc.ABCMeta)
class TileCollection(object):
    """
    Abstract class used to describe an object that can contain a list of
    :py:class:`~draftsman.classes.tile.Tile` instances.
    """

    @abc.abstractproperty
    def tiles(self):  # pragma: no coverage
        """
        Object that holds the ``Tiles``, usually a
        :py:class:`~draftsman.classes.tilelist.TileList`.
        """
        pass

    @abc.abstractproperty
    def tile_hashmap(self):  # pragma: no coverage
        """
        Object that holds the spatial information for the Tiles of this object,
        usually a :py:class:`~draftsman.classes.spatialhashmap.SpatialHashMap`.
        """
        pass

    # =========================================================================
    # Queries
    # =========================================================================

    def find_tile(self, x, y):
        # type: (int, int) -> Tile
        """
        Returns the tile at the tile-coordinate ``x`` and ``y``. If there are
        multiple tiles at that location, the entity that was inserted first is
        returned.

        :param x: X-position in tile-coordinates to search.
        :param y: Y-position in tile-coordinates to search.

        :returns: The tile at ``(x, y)``, or ``None`` if there is none.
        """
        tiles = self.tile_hashmap.get_on_point((x + 0.5, y + 0.5))
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
              - ``[float, float]`` or ``{"x": float, "y": float}``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``[[float, float], [float, float]]``
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
