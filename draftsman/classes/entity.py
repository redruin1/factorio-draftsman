# entity.py
# -*- encoding: utf-8 -*-

# Long term:
# TODO: defaults!
# TODO: "succinct" mode for to_dict(), integrate with better default management
# TODO: flipping and rotation of entities

from __future__ import unicode_literals

from draftsman.classes.association import Association
from draftsman.classes.collisionset import CollisionSet
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.vector import Vector
from draftsman.data import entities
from draftsman.error import InvalidEntityError, DraftsmanError
from draftsman import utils

import copy
from typing import Union, Callable
import six


class Entity(EntityLike):
    """
    Entity base-class. Used for all entity types that are specified in Factorio.
    Categorizes entities into "types" based on their class, each of which is
    implemented in :py:mod:`draftsman.prototypes`.
    """

    def __init__(self, name, similar_entities, tile_position=[0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        """
        Constructs a new Entity. All prototypes have this entity as their most
        Parent class.

        Raises :py:class:`draftsman.warning.DraftsmanWarning` for every unused
        keyword passed into the constructor.

        :param name: The name of the entity. Must be one of ``similar_entities``.
        :param similar_entities: A list of valid names associated with this
            Entity class. Can be though of as a list of all the entities of this
            type.
        :param tile_position: The tile position to set the entity to. Defaults
            to the origin.
        :param kwargs: Any other valid parameters to set.

        :exception InvalidEntityError: If ``name`` is set to anything other than
            an entry in ``similar_entities``.
        """
        # Init EntityLike
        super(Entity, self).__init__()
        # Create a set of keywords that transfer in to_dict function
        # Since some things we want to keep internal without sending to to_dict
        self.exports = dict()
        # For user convinience, keep track of all the unused arguments, and
        # issue a warning if the user provided one that was not used.
        self.unused_args = kwargs

        # Entities of the same type
        self.similar_entities = similar_entities

        # Name
        if name not in self.similar_entities:
            raise InvalidEntityError(
                "'{}' is not a valid name for this {}".format(
                    name, self.__class__.__name__
                )
            )
        self._name = six.text_type(name)
        self._add_export("name")

        # Entity type
        self._type = entities.raw[self.name]["type"]

        # ID (used in Blueprints and Groups)
        self.id = None
        if "id" in kwargs:
            self.id = kwargs["id"]
            self.unused_args.pop("id")

        # TODO: technically there's no reason each individual entity needs it's
        # own copy of it's collision set, (aside from rotation)
        # Therefore it would be more efficient to create a lookup table where
        # each Entity type would get the root copy of the data and then
        # transform it when needed (less performant maybe?)

        # Collision set (Internal)
        # Check to see if we have overwritten this value with the better ones
        if not hasattr(self, "_overwritten_collision_set"):
            collision_box = entities.raw[self.name]["collision_box"]
            self._collision_set = CollisionSet(
                [
                    utils.AABB(
                        collision_box[0][0],
                        collision_box[0][1],
                        collision_box[1][0],
                        collision_box[1][1],
                    )
                ]
            )

        # Collision mask (Internal)
        if "collision_mask" in entities.raw[self.name]:
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # Base default
            self._collision_mask = {
                "item-layer",
                "object-layer",
                "player-layer",
                "water-tile",
            }

        # Tile Width and Height (Internal)
        # Usually tile dimensions are implicitly based on the collision box
        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self._collision_set.get_bounding_box()
        )
        # But sometimes it can be overrided in special cases (rails)
        if "tile_width" in entities.raw[self.name]:
            self._tile_width = entities.raw[self.name]["tile_width"]
        if "tile_height" in entities.raw[self.name]:
            self._tile_height = entities.raw[self.name]["tile_height"]

        # Hidden? (Internal)
        self._hidden = "hidden" in entities.raw[self.name]["flags"]

        # Position
        if "position" in kwargs:
            self.position = kwargs["position"]
            self.unused_args.pop("position")
        else:
            self.tile_position = tile_position
        self._add_export(
            "global_position", None, lambda k, v: ("position", v.to_dict())
        )

        # Entity tags
        self.tags = {}
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
            self.unused_args.pop("tags")
        self._add_export("tags", lambda x: x)

        # Remove entity_number if we're importing from a dict
        self.unused_args.pop("entity_number", None)

    # =========================================================================

    @property
    def name(self):
        # type: () -> str
        """
        The name of the entity. Must be a valid Factorio ID string. Read only.

        :type: ``str``
        """
        return self._name

    # @name.setter
    # def name(self, value):
    #     # type: (str) -> None
    #     if self.parent:
    #         raise DraftsmanError(
    #             "Cannot change name of entity while in another collection"
    #         )

    #     if value in self.similar_entities:
    #         self._name = value
    #     else:
    #         raise InvalidEntityError("'{}' is not a valid name for this type"
    #                                  .format(value))

    # =========================================================================

    @property
    def type(self):
        # type: () -> str
        """
        The type of the Entity. Equivalent to the key found in Factorio's
        ``data.raw``. Mostly equivalent to the type of the entity instance,
        though there are some differences,
        :ref:`as noted here <handbook.entities.differences>`.
        Can be used as a criteria to search with in
        :py:meth:`.EntityCollection.find_entities_filtered`.
        Not exported; read only.

        :type: ``str``
        """
        return self._type

    # =========================================================================

    @property
    def id(self):
        # type: () -> str
        """
        A unique string ID associated with this entity. ID's can be anything,
        though there can only be one entity with a particular ID in an
        EntityCollection. Not exported.

        :getter: Gets the ID of the entity, or ``None`` if the entity has no ID.
        :setter: Sets the ID of the entity.
        :type: ``str``

        :exception TypeError: If the set value is anything other than a ``str``
            or ``None``.
        :exception DuplicateIDError: If the ID is changed while inside an
            ``EntityCollection`` to an ID that is already taken by another
            entity in said ``EntityCollection``.
        """
        return self._id

    @id.setter
    def id(self, value):
        # type: (str) -> None
        if value is None:
            if self.parent:
                self.parent.entities.remove_key(self._id)
            self._id = value
        elif isinstance(value, six.string_types):
            old_id = self._id
            self._id = six.text_type(value)
            if self.parent:
                self.parent.entities.remove_key(old_id)
                self.parent.entities.set_key(self._id, self)
        else:
            raise TypeError("'id' must be a str or None")

    # =========================================================================

    @property
    def position(self):
        # type: () -> Vector
        """
        The "canonical" position of the Entity, or the one that Factorio uses.
        Positions of most entities are located at their center, which can either
        be in the middle of a tile or on it's transition, depending on the
        Entity's ``tile_width`` and ``tile_height``.

        ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
        keys, or more succinctly as a sequence of floats, usually a ``list`` or
        ``tuple``. ``position`` can also be specified more verbosely as a
        ``Vector`` instance as well.

        This property is updated in tandem with ``tile_position``, so using them
        both interchangeably is both allowed and encouraged.

        :getter: Gets the position of the Entity.
        :setter: Sets the position of the Entity.
        :type: :py:class:`.Vector`

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple, Vector]) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of entity while it's inside another object"
            )

        self._position = Vector.from_other(value, float)

        # try:
        #     self._position = Vector.from_other({"x": float(value["x"]), "y": float(value["y"])})
        # except TypeError:
        #     self._position = {"x": float(value[0]), "y": float(value[1])}

        grid_x = round(self._position.x - self.tile_width / 2.0)
        grid_y = round(self._position.y - self.tile_height / 2.0)
        # self._tile_position = {"x": grid_x, "y": grid_y}
        self._tile_position = Vector(grid_x, grid_y)

    # =========================================================================

    @property
    def tile_position(self):
        # type: () -> Vector
        """
        The tile-position of the Entity. The tile position is the position
        according the the LuaSurface tile grid, and is the top left corner of
        the top-leftmost tile of the Entity.

        ``tile_position`` can be specified as a ``dict`` with ``"x"`` and
        ``"y"`` keys, or more succinctly as a sequence of floats, usually a
        ``list`` or ``tuple``.

        This property is updated in tandem with ``position``, so using them both
        interchangeably is both allowed and encouraged.

        :getter: Gets the tile position of the Entity.
        :setter: Sets the tile position of the Entity.
        :type: :py:class:`.Vector`

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._tile_position

    @tile_position.setter
    def tile_position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of entity while it's inside another object"
            )

        self._tile_position = Vector.from_other(value, int)

        # try:
        #     self._tile_position = {
        #         "x": math.floor(value["x"]),
        #         "y": math.floor(value["y"]),
        #     }
        # except TypeError:
        #     self._tile_position = {"x": math.floor(value[0]), "y": math.floor(value[1])}

        absolute_x = self._tile_position.x + self.tile_width / 2.0
        absolute_y = self._tile_position.y + self.tile_height / 2.0
        # self._position = {"x": absolute_x, "y": absolute_y}
        self._position = Vector(absolute_x, absolute_y)

    # =========================================================================

    @property
    def global_position(self):
        # type: () -> dict
        """
        The "global", or root-most position of the Entity. This value is always
        equivalent to :py:meth:`~.Entity.position`, unless the entity exists
        inside an :py:class:`.EntityCollection`. If it does, then it's global
        position is equivalent to the sum of all parent positions plus it's own
        position. For example, if an Entity exists within a :py:class:`.Group`
        at position ``(5, 5)`` and the ``Group`` exists at ``(5, 5)``, the
        ``global_position`` of the Entity will be ``(10, 10)``.

        This is used to get an entity's "actual" position in a blueprint, used
        when adding to a :py:class:`.SpatialHashMap` and when querying the
        entity by region. This attribute is always exported, but renamed to
        "position"; read only.

        :type: ``dict{"x": float, "y": float}``
        """
        if self.parent and hasattr(self.parent, "global_position"):
            return self.parent.global_position + self.position
        else:
            return self.position

    # =========================================================================

    # @property
    # def collision_box(self):
    #     # type: () -> list
    #     """
    #     The AABB that stores the collision area of the Entity. Equivalent to
    #     the one specified in Factorio's ``data.raw``. Not exported; read only.

    #     The ``collision_box`` treats the Entity's position as the origin. This
    #     means that it is position independent, and equivalent for all entities
    #     with the same name. If you want to know the area the Entity occupies in
    #     world-space, you can use :py:meth:`get_area` instead.

    #     :type: ``[[float, float], [float, float]]``
    #     """
    #     return self._collision_box

    @property
    def collision_set(self):
        # type: () -> CollisionSet
        """
        TODO
        """
        return self._collision_set

    # =========================================================================

    @property
    def collision_mask(self):
        # type: () -> set
        """
        The set of all collision layers that this Entity collides with,
        specified as strings. Equivalent to Factorio's ``data.raw`` equivalent.
        Not exported; read only.

        :type: ``set{str}``
        """
        return self._collision_mask

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        The width of the entity in tiles, rounded up to the nearest integer.
        Not exported; read only.

        :type: ``int``
        """
        return self._tile_width

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        The height of the entity in tiles, rounded up to the nearest integer.
        Not exported; read only.

        :type: ``int``
        """
        return self._tile_height

    # =========================================================================

    @property
    def hidden(self):
        # type: () -> bool
        """
        Whether or not this Entity is considered "hidden", as specified in it's
        flags in Factorio's ``data.raw``. Not exported; read only.

        .. NOTE::

            "Hidden" in this context is somewhat unintuitive, as items you might
            think would be considered hidden may not be. Ship wreckage entities,
            for example, are not considered "hidden", even though the only way
            to access them is with the editor. Keep this in mind when querying
            this attribute, especially since this discrepancy might be
            considered a bug later on.

        .. seealso::

            `<https://wiki.factorio.com/Types/EntityPrototypeFlags>`_

        :type: ``bool``
        """
        return self._hidden

    # =========================================================================

    @property
    def flippable(self):
        # type: () -> bool
        """
        Whether or not this entity can be mirrored in game using 'F' or 'G'.
        Not exported; read only.

        .. NOTE::

            Work in progress. May be incorrect, especially for modded entities.
        """
        return entities.flippable[self.name]

    # =========================================================================

    @property
    def tags(self):
        # type: () -> dict
        """
        Tags associated with this Entity. Commonly used by mods to add custom
        data to a particular Entity when exporting and importing Blueprint
        strings.

        :getter: Gets the tags of the Entity, or ``None`` if not set.
        :setter: Sets the Entity's tags.
        :type: ``dict{Any: Any}``

        :exception TypeError: If tags is set to anything other than a ``dict``
            or ``None``.
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        # type: (dict) -> None
        if tags is None or isinstance(tags, dict):
            self._tags = tags
        else:
            raise TypeError("'tags' must be a dict or None")

    # =========================================================================

    def to_dict(self):
        # type: () -> dict
        """
        Converts the Entity to its JSON dict representation. The keys returned
        are determined by the contents of the `exports` dictionary and their
        criteria functions.

        A attribute from the Entity will be included as a key in the output dict
        if both of the following conditions are met:

        1. The attribute is in the ``exports`` dictionary
        2. The associated criteria function is either not present or returns
           ``True``. This is used to avoid including excess keys, keeping
           Blueprint string size down.

        In addition, a second function may be provided to have a formatting step
        to alter either the key and/or its value, which gets inserted into the
        output ``dict``.

        :returns: The exported JSON-dict representation of the Entity.
        """
        # Only add the keys in the exports dictionary
        out = {}
        for name, funcs in self.exports.items():
            value = getattr(self, name)
            criterion = funcs[0]
            formatter = funcs[1]
            # Does the value match the criteria to be included?
            if criterion is None or criterion(value):
                if formatter is not None:
                    # Normalize key/value pair
                    k, v = formatter(name, value)
                else:
                    k, v = name, value
                out[k] = v

        return out

    def mergable_with(self, other):
        # type: (Entity) -> bool
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.global_position == other.global_position
            and self.id == other.id
        )

    def merge(self, other):
        # type: (Entity) -> None
        # TODO: It might be smarter to just move all these into thier own mixins;
        # that way we wouldn't have to call hasattr() for all of them

        # Control Behavior (overwrite self with other)
        if hasattr(self, "control_behavior") and hasattr(other, "control_behavior"):
            # TODO: set on per entity basis
            self.control_behavior = copy.deepcopy(other.control_behavior)

        # Power Neighbours (union of the two sets, not exceeding 5 connections)
        if hasattr(self, "neighbours") and hasattr(other, "neighbours"):
            # Iterate over every association in other (the to-be deleted entity)
            for association in other.neighbours:
                # Keep track of whether or not this association was added to self
                association_added = False

                # Make sure we don't add the same association multiple times
                if association not in self.neighbours:
                    # Also make sure we don't exceed 5 connections
                    if len(self.neighbours) < 5:
                        self.neighbours.append(association)
                        association_added = True

                # However, entities that used to point to `other` still do,
                # which causes problems since `other` is usually to be deleted
                # after merging
                # So we now we find the entity that other used to point to and
                # iterate over it's neighbours:
                associated_entity = association()
                for i, old_association in enumerate(associated_entity.neighbours):
                    # If the association used to point to `other`, make it point
                    # to `self`
                    if old_association == Association(other):
                        # Only do so, however, if this association is not
                        # already in the set of neighbours and we added the
                        # connection before, and if we actually even merged the
                        # connection in the first place
                        if (
                            Association(self) not in associated_entity.neighbours
                            and association_added
                        ):
                            associated_entity.neighbours[i] = Association(self)
                        else:
                            # Otherwise, the association points to an entity
                            # that will likely become invalid, so we remove it
                            associated_entity.neighbours.remove(old_association)

        def merge_circuit_connection(self, side, color, point, other):
            # Keep track of whether or not this association was added to self
            association_added = False

            # Make sure we don't add the same association multiple times
            if point not in self.connections[side][color]:
                self.connections[side][color].append(point)
                association_added = True

            # Determine the location where `point` points to
            association = point["entity_id"]
            associated_entity = association()
            target_side = point.get("circuit_id", 1)  # default to `1` if not there
            if associated_entity.dual_circuit_connectable:
                target = {"entity_id": Association(self), "circuit_id": target_side}
            else:
                target = {"entity_id": Association(self)}

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
        #         print("what the fuck")

        # Connections (union of the two sets)
        if hasattr(self, "connections") and hasattr(other, "connections"):
            for side in other.connections:
                if side in {"1", "2"}:
                    if side not in self.connections:
                        self.connections[side] = {}
                    for color in other.connections[side]:
                        if color not in self.connections[side]:
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
                        "Cannot merge power switches (yet); see <TODO> for details"
                    )

        # Tags (overwrite self with other)
        # (make sure to make a copy in case the original data gets deleted)
        self.tags = copy.deepcopy(other.tags)

    def _add_export(self, name, criterion=None, formatter=None):
        # type: (str, Callable, Callable) -> None
        """
        Adds a key to ``exports`` with an optional criteria and formatting
        function.

        We can't just convert the entire entity to a dict, because there are a
        number of keys (for technical or space reasons) that we dont want to
        add to the dictionary. Instead, we keep track of the keys we do want
        (``exports``) and add those if they're present in the Entity object.

        However, some items that are present in Entity might be initialized to
        ``None`` or otherwise redundant values, which would just take up space
        in the output dict. Hence, we can also provide a criteria function that
        takes a single argument, the value of the element in the `Entity`. If
        the function returns ``True``, the key is added to the output dictionary.
        If the function is ``None``, the key is always added.

        This function also supports an optional ``formatter`` function that
        takes two arguments, the ``key`` and ``value`` pair and returns a tuple
        of the two in the same order. This allows to perform any modification to
        the key or value before being added to the output dict.

        :param name: The name of the attribute that you would like to keep.
        :param criterion: Function that determines whether or not the attribute
            should be added.
        :param formatter: Function that determines the output format of the
            key-value pair in the output dictionary.
        """
        self.exports[name] = [criterion, formatter]

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        return "<{0}{1}>{2}".format(
            type(self).__name__,
            " '{}'".format(self.id) if self.id is not None else "",
            str(self.to_dict()),
        )
        # Association debug printing
        # return "<{0}{1} at 0x{2:016X}>{3}".format(
        #     type(self).__name__,
        #     " '{}'".format(self.id) if self.id is not None else "",
        #     id(self),
        #     str(self.to_dict()),
        # )
