# group.py
# -*- encoding: utf-8 -*-

# TODO: documentation!

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

    groups can have unique name and id:
        "grouptype1", id = "A"
        "grouptype2", id = "B"
        "grouptype3", id = "C"

    ```
    # This would only get groups with name "grouptype1"
    entities = blueprint.find_entities_filtered(name = "grouptype1")
    # This would get the one group with id "A"
    entity = blueprint.find_entity_by_id("A")
    # This would get all default groups
    entities = blueprint.find_entities_filtered(type = "group")
    ```
    """

    def __init__(self, id, name="group", type="group", position=(0, 0), entities=[]):
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
        TODO
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
        """ """
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
        """ """
        return self._id

    @id.setter
    def id(self, value):
        # type: (str) -> None
        if isinstance(value, six.string_types):
            old_id = getattr(self, "id", None)
            self._id = six.text_type(value)

            # Modify parent EntityList key_map
            if self.parent:
                self.parent.entities.remove_key(old_id)
                self.parent.entities.set_key(self.id, self)
        else:
            raise TypeError("'id' must be a str")

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        TODO
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[list, dict]) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of Group while it's inside another object"
            )

        try:
            self._position = {"x": float(value["x"]), "y": float(value["y"])}
        except TypeError:
            self._position = {"x": float(value[0]), "y": float(value[1])}

    # =========================================================================

    @property
    def collision_box(self):
        # type: () -> list
        """
        TODO
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
        TODO
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
        TODO
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
        """ """
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
    def entities(self):
        # type: () -> EntityList
        """
        Docstring?
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
        return self._entity_hashmap

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True
        return False

    # =========================================================================

    @property
    def rotatable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return True

    # =========================================================================

    @property
    def flippable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        # TODO: uncomment
        # for entity in self.entities:
        #     if not entity.flippable:
        #         return False
        return True

    # =========================================================================

    def on_entity_insert(self, entitylike):
        # type: (EntityLike) -> None
        """
        Function called when an entity is added to the Group's EntityList.
        Handles the spatial hashmap and updates the positions collision_box
        of the entity.
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
        """ """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(old_entitylike)
        # Add the new entity and its children
        self.entity_hashmap.recursively_add(new_entitylike)

    def on_entity_remove(self, entitylike):
        # type: (EntityLike) -> None
        """ """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(entitylike)

    # =========================================================================

    def get(self):
        """ """

        def flatten_entities(entities):
            out = []
            for entity in entities:
                result = entity.get()
                if isinstance(result, list):
                    out.extend(flatten_entities(result))
                else:
                    out.append(result)
            return out

        out = flatten_entities(self.entities)

        for out_entity in out:
            # Offset the Entity's position by the Group's position
            out_entity.position["x"] += self.position["x"]
            out_entity.position["y"] += self.position["y"]
            # Adjust entity id (internally)
            # if out_entity._id:
            #     if isinstance(out_entity._id, tuple):
            #         old_id_list = [self.id, *out_entity._id]
            #         out_entity._id = tuple(old_id_list)
            #     else:
            #         out_entity._id = (self.id, out_entity._id)

        return out

    def recalculate_area(self):
        # type: () -> None
        """
        Recalculates the dimensions of the area and tile_width and
        height. Called when an EntityLike or Tile object is altered or removed.
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

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        return "<Group>" + str(self.entities.data)
