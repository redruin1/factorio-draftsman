# group.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entitylist import EntityList
from draftsman.classes.collection import EntityCollection
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.spatialhashmap import SpatialHashMap
from draftsman.classes.transformable import Transformable
from draftsman.error import DraftsmanError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import DraftsmanWarning

from typing import Union
import six


class Group(Transformable, EntityCollection, EntityLike):
    """
    Group entities together, so you can manipulate them all as one unit.

    Allows for the creation of "blocks" that can be added multiple times very
    easily to a blueprint. This allows you to create a section with complex
    circuit connections, and then add that ``Group`` multiple times and the
    circuit connections will be the same for every block with no extra work.

    Groups can also be used to organize Blueprints at the structure level. You
    can give entities the same name in a Blueprint as long as they exist in
    different groups. For example, the following is a perfectly valid structure
    for a Blueprint to have:

    .. code-block::

        <Blueprint>.entities => [
            <Group "1">.entities => [<Entity "A">, <Entity "B">, <Entity "C">],
            <Group "2">.entities => [<Entity "A">, <Entity "B">, <Entity "C">],
        ]

    This is particularly useful if each group has a similar function, but just
    exists as a different "part" of the overall blueprint.

    To aid in quickly accessing nested entities in such structures,
    ``EntityLists`` support indexing with a sequence, usually a tuple. For
    example, assuming the Blueprint structure above, all of the following
    assertions are true:

    .. code-block:: python

        assert blueprint.entities[("1", "A")].id == "A"
        assert isinstance(blueprint.entities[("2", "A")], Entity)
        assert blueprint.entities[("1", "C")] is blueprint.entities["1"].entities["C"]

    ``EntityLike`` instances in a Group are considered to be in "group-space";
    meaning their positions are offset by the position of the Group they reside
    in. If a Group is located at position ``(5, 5)``, and an entity inside of it
    is located at ``(5, 5)``, when added to a Blueprint the entity will be
    located at ``(10, 10)``. This effect continues if Groups nest inside of
    other Groups, which is also perfectly legal.

    Groups have their own ``SpatialHashMap`` instances, so they will issue
    :py:class:`~draftsman.warning.OverlappingObjectsWarning` when entities
    overlap, both when adding entities to the Group and when adding the Group to
    another ``EntityCollection``.
    """

    @utils.reissue_warnings
    def __init__(
        self, id=None, name="group", type="group", position=(0, 0), entities=[]
    ):
        # type: (str, str, str, Union[dict, list, tuple], list) -> None
        super(Group, self).__init__()  # EntityLike

        self.id = id

        self.name = name
        self.type = type
        self.position = position

        self._entity_hashmap = SpatialHashMap()

        # Collision box
        self.collision_box = None

        # Tile dimensions
        self.tile_width, self.tile_height = 0, 0

        # Collision mask
        self.collision_mask = None  # empty set()

        # List of entities
        self.entities = entities

    # =========================================================================

    @property
    def name(self):
        # type: () -> str
        """
        The name of the Group. Defaults to ``"group"``. Can be specified to any
        string to aid in organization. For example:

        .. code-block:: python

            blueprint.entities.append(Group("A"))
            blueprint.entities.append(Group("B", name="different_name"))

            diff = blueprint.find_entities_filtered(name="different_name")
            assert diff[0] is blueprint.entities["B"]

        :getter: Gets the name of the Group.
        :setter: Sets the name of the Group.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str``.
        """
        return self._name

    @name.setter
    def name(self, value):
        # type: (str) -> None
        if isinstance(value, six.string_types):
            self._name = six.text_type(value)
        else:
            raise TypeError("'name' must be a str")

    # =========================================================================

    @property
    def type(self):
        # type: () -> str
        """
        The type of the Group. Defaults to ``"group"``. Can be specified to any
        string to aid in organization. For example:

        .. code-block:: python

            blueprint.entities.append(Group("A"))
            blueprint.entities.append(Group("B", type="different_type"))

            diff = blueprint.find_entities_filtered(type="different_type")
            assert diff[0] is blueprint.entities["B"]

        :getter: Gets the type of the Group.
        :setter: Sets the type of the Group.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str``.
        """
        return self._type

    @type.setter
    def type(self, value):
        # type: (str) -> None
        if isinstance(value, six.string_types):
            self._type = six.text_type(value)
        else:
            raise TypeError("'type' must be a str")

    # =========================================================================

    @property
    def id(self):
        # type: () -> str
        """
        The ID of the Group. The most local form of identification between
        Groups.

        :getter: Gets the ID of the Group.
        :setter: Sets the ID of the Group.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return self._id

    @id.setter
    def id(self, value):
        # type: (str) -> None
        if value is None or isinstance(value, six.string_types):
            old_id = getattr(self, "id", None)
            self._id = six.text_type(value) if value is not None else value

            # Modify parent EntityList key_map
            if self.parent:
                self.parent.entities.remove_key(old_id)
                self.parent.entities.set_key(self.id, self)
        else:
            raise TypeError("'id' must be a str or None")

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        The position of the Group. Acts as the origin of all the entities
        contained within, and offsets them on export.

        ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
        keys, or more succinctly as a sequence of floats, usually a ``list`` or
        ``tuple``.

        :getter: Gets the position of the Group.
        :setter: Sets the position of the Group.
        :type: ``dict{"x": float, "y": float}``

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the Group's position is modified when
            inside a EntityCollection, :ref:`which is forbidden
            <handbook.blueprints.forbidden_entity_attributes>`.
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[list, dict]) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of Group while it's inside a Collection"
            )

        if "x" in value and "y" in value:
            self._position = {"x": float(value["x"]), "y": float(value["y"])}
        elif isinstance(value, (list, tuple)):
            self._position = {"x": float(value[0]), "y": float(value[1])}
        else:
            raise TypeError("Incorrectly formatted position ({})".format(value))

    # =========================================================================

    @property
    def global_position(self):
        # type: () -> dict
        """
        The "global", or root-most position of the Group. This value is always
        equivalent to :py:attr:`~.Group.position`, unless the group exists
        inside another :py:class:`.EntityCollection`. If it does, then it's
        global position is equivalent to the sum of all parent positions plus
        it's own position. Used when recursing the position of any sub-entity
        contained within the ``Group``. Read only.

        :type: ``dict{"x": float, "y": float}``
        """
        if self.parent and hasattr(self.parent, "global_position"):
            return {
                "x": self.parent.global_position["x"] + self.position["x"],
                "y": self.parent.global_position["y"] + self.position["y"],
            }
        else:
            return self.position

    # =========================================================================

    @property
    def collision_box(self):
        # type: () -> list
        """
        The union of all the ``collision_box``s of the entities that this Group
        holds. Adding an entity to the Group sets the collision box to the
        minimum bounding box of the Group and the added Entity. If an Entity is
        changed or removed inside the Group, the ``collision_box`` is
        reconstructed from scratch. Read only.

        :type: ``[[float, float], [float, float]]``
        """
        return self._collision_box

    @collision_box.setter
    def collision_box(self, value):
        # type: (list) -> None
        self._collision_box = signatures.AABB.validate(value)

    # =========================================================================

    @property
    def collision_mask(self):
        # type: () -> set
        """
        The set of all collision layers that this Entity collides with,
        specified as strings. Defaults to an empty ``set``. Not exported.

        :getter: Gets the collision mask of the Group.
        :setter: Sets the collision mask of the Group, or sets it to an empty
            set if ``None`` was input.
        :type: ``set{str}``

        :exception TypeError: If set to anything other than a `set` or None.
        """
        return self._collision_mask

    @collision_mask.setter
    def collision_mask(self, value):
        # type: (set) -> None
        if value is None:
            self._collision_mask = set()
        elif isinstance(value, set):
            self._collision_mask = value
        else:
            raise TypeError("'collision_mask' must be a set or None")

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        The width of the Group's ``collision_box``, rounded up to the nearest
        tile. Read only.

        :type: ``int``
        """
        return self._tile_width

    @tile_width.setter
    def tile_width(self, value):
        # type: (int) -> None
        if isinstance(value, six.integer_types):
            self._tile_width = value
        else:
            raise TypeError("'tile_width' must be an int")

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        The width of the Group's ``collision_box``, rounded up to the nearest
        tile. Read only.

        :type: ``int``
        """
        return self._tile_height

    @tile_height.setter
    def tile_height(self, value):
        # type: (int) -> None
        if isinstance(value, six.integer_types):
            self._tile_height = value
        else:
            raise TypeError("'tile_height' must be an int")

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True
        return False

    # =========================================================================

    @property
    def entities(self):
        # type: () -> EntityList
        """
        The list of the Group's entities. Internally the list is a custom
        class named :py:class:`draftsman.classes.EntityList`, which has all the
        normal properties of a regular list, as well as some extra features.
        For more information on ``EntityList``, check out this writeup
        :ref:`here <handbook.blueprints.blueprint_differences>`.
        """
        return self._entities

    @entities.setter
    @utils.reissue_warnings
    def entities(self, value):
        # type: (list[EntityLike]) -> None
        if value is None:
            self._entity_hashmap.clear()
            self._entities.clear()
        elif isinstance(value, list):
            self._entity_hashmap.clear()
            self._entities = EntityList(self, value)
        elif isinstance(value, EntityList):
            value._parent = self
            self._entities = value
        else:
            raise TypeError("'entities' must be an EntityList, list, or None")

    # =========================================================================

    @property
    def entity_hashmap(self):
        # type: () -> SpatialHashMap
        """
        The ``SpatialHashMap`` for ``entities``. Not exported; read only.
        """
        return self._entity_hashmap

    # =========================================================================

    def on_entity_insert(self, entitylike):
        # type: (EntityLike) -> None
        """
        Callback function for when an ``EntityLike`` is added to this
        Group's ``entities`` list. Handles the addition of the entity into
        the  Group's ``SpatialHashMap``, and recalculates it's dimensions.
        """
        # Add to hashmap (as well as any children)
        self.entity_hashmap.recursively_add(entitylike)

        # Update dimensions
        self._collision_box = utils.extend_aabb(
            self._collision_box, entitylike.get_area()
        )
        (
            self._tile_width,
            self._tile_height,
        ) = utils.aabb_to_dimensions(self.collision_box)

    def on_entity_set(self, old_entitylike, new_entitylike):
        # type: (EntityLike, EntityLike) -> None
        """
        Callback function for when an entity is overwritten in a Group's
        ``entities`` list. Handles the removal of the old ``EntityLike`` from
        the ``SpatialHashMap`` and adds the new one in it's stead.
        """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(old_entitylike)
        # Add the new entity and its children
        self.entity_hashmap.recursively_add(new_entitylike)

    def on_entity_remove(self, entitylike):
        # type: (EntityLike) -> None
        """
        Callback function for when an entity is removed from a Blueprint's
        ``entities`` list. Handles the removal of the ``EntityLike`` from the
        ``SpatialHashMap``.
        """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(entitylike)

    # =========================================================================

    def get(self):
        """
        Gets all the child-most ``Entity`` instances in this ``Group`` and
        returns them as a "flattened" 1-dimensional list. Offsets all of their
        positions by the position of the parent ``Group``.

        :returns: A ``list`` of ``Entity`` instances associated with this
            ``Group``.
        """
        return utils.flatten_entities(self.entities)

    def recalculate_area(self):
        # type: () -> None
        """
        Recalculates the dimensions of the area and tile_width and
        height. Called when an ``EntityLike`` object is altered or removed.
        """
        self._collision_box = None
        for entity in self.entities:
            self._collision_box = utils.extend_aabb(
                self._collision_box, entity.get_area()
            )

        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self._collision_box
        )

    def get_area(self):
        # type: () -> list
        collision_box = (
            [[0, 0], [0, 0]] if self.collision_box is None else self.collision_box
        )
        return [
            [
                collision_box[0][0] + self.position["x"],
                collision_box[0][1] + self.position["y"],
            ],
            [
                collision_box[1][0] + self.position["x"],
                collision_box[1][1] + self.position["y"],
            ],
        ]

    def __str__(self):  # pragma: no coverage
        # type: () -> str
        return "<Group>" + str(self.entities.data)
