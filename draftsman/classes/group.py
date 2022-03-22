# group.py

# TODO: documentation!

from draftsman.classes.entitylike import EntityLike
from draftsman.error import InvalidEntityError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import DraftsmanWarning

from schema import SchemaError
from typing import Union
import warnings


class Group(EntityLike):
    """
    Group entities together, so you can move and access them all as one unit.

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
    def __init__(self, name: str = "group", **kwargs):
        # type: (str, **dict) -> None
        super(Group, self).__init__()

        # For user convinience, keep track of all the unused arguments, and 
        # issue a warning if the user provided one that was not used.
        # TODO: find a more elegant solution for this functionality
        self.unused_args = kwargs

        self.name = name

        self.type = "group"
        if "type" in kwargs:
            self.type = kwargs["type"]
            self.unused_args.pop("type")

        self.id = None
        if "id" in kwargs:
            self.id = kwargs["id"]
            self.unused_args.pop("id")

        self.position = [0, 0]
        if "position" in kwargs:
            self.position = kwargs["position"]
            self.unused_args.pop("position")
            

        # Collision box
        self.collision_box = None

        # Tile dimensions
        self.tile_width, self.tile_height = 0, 0

        # List of entities
        self.entities = []
        if "entities" in kwargs:
            self.entities = kwargs["entities"]
            self.unused_args.pop("entities")
            #self.set_entities(kwargs["entities"])

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

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
        if value is None or isinstance(value, str):
            self._name = value
        else:
            raise TypeError("'name' must be a str")

    # =========================================================================

    @property
    def type(self):
        # type: () -> str
        """
        """
        return self._type

    @type.setter
    def type(self, value):
        # type: (str) -> None
        if value is None or isinstance(value, str):
            self._type = value
        else:
            raise TypeError("'type' must be a str or None")

    # =========================================================================

    @property
    def id(self):
        # type: () -> str
        """
        """
        return self._id

    @id.setter
    def id(self, value):
        # type: (str) -> None
        if value is None or isinstance(value, str):
            self._id = value
        else:
            raise TypeError("'id' must be a str or None")

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[list, dict]) -> None
        # TODO: there is a better way to do this
        try:
            position = signatures.POSITION.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid position format")
        if isinstance(position, list):
            self._position = {"x": position[0], "y": position[1]}
        elif isinstance(position, dict): # pragma: no branch
            self._position = position

    # =========================================================================

    @property
    def collision_box(self):
        # type: () -> list
        """
        """
        return self._collision_box

    @collision_box.setter
    def collision_box(self, value):
        # type: (list) -> None
        self._collision_box = signatures.AABB.validate(value)

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        """
        return self._tile_width

    @tile_width.setter
    def tile_width(self, value):
        # type: (int) -> None
        self._tile_width = signatures.INTEGER.validate(value)

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        """
        return self._tile_height

    @tile_height.setter
    def tile_height(self, value):
        # type: (int) -> None
        self._tile_height = signatures.INTEGER.validate(value)

    # =========================================================================

    @property
    def entities(self):
        # type: () -> list[EntityLike]
        """
        Docstring?
        """
        return self._entities

    @entities.setter
    def entities(self, value):
        # type: (list[EntityLike]) -> None
        for entity in value:
            # Ensure that all entries are EntityLikes
            if not isinstance(entity, EntityLike):
                raise InvalidEntityError(entity)
            # Calculate new dimensions
            if self.collision_box is None:
                self._collision_box = entity.get_area()
            else:
                self._collision_box = utils.extend_aabb(
                    self.collision_box, 
                    entity.get_area()
                )

        if self.collision_box:
            self._tile_width, self._tile_height = utils.aabb_to_dimensions(
                self.collision_box
            )

        self._entities = value

    # =========================================================================

    def add_entity(self, entity):
        # type: (EntityLike) -> None
        """
        Add an entity to the group.
        """
        if not isinstance(entity, EntityLike):
            raise InvalidEntityError(entity)

        # Modify Group dimensions
        if self.collision_box is None:
            self.collision_box = entity.get_area()
        else:
            self._collision_box = utils.extend_aabb(
                self.collision_box, 
                entity.get_area()
            )
        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self.collision_box
        )

        self._entities.append(entity)

    def remove_entity(self, entity):
        # type: (EntityLike) -> None
        """
        Remove the specific entity from the Group.
        """
        self.entities.remove(entity)

        # Recalcualte Group dimensions
        self.collision_box = None
        for old_entity in self.entities:
            if self.collision_box is None:
                self.collision_box = old_entity.get_area()
            else:
                self._collision_box = utils.extend_aabb(
                    self.collision_box, 
                    old_entity.get_area()
                )
            
        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self.collision_box
        )

    # =========================================================================

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the group.
        """
        return [[self.collision_box[0][0] + self.position["x"],
                 self.collision_box[0][1] + self.position["y"]],
                [self.collision_box[1][0] + self.position["x"],
                 self.collision_box[1][1] + self.position["y"]]]

    def to_dict(self):
        # type: () -> list[dict]
        """
        Converts the group to JSON representation. Returns a list of dicts,
        where each dict represents a valid EntityLike representation.
        """
        out = []
        for entity in self.entities:
            # Offset the entities position by the groups position
            out.append(entity.to_dict())
        
        return out

    def __repr__(self):
        # type: () -> str
        return "<Group>" + str(self.entities)