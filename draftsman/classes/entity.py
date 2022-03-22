# entity.py

# TODO: make sure that all functions that modify the entity preserve the 
#       entity's contents when they throw an error
# TODO: change all instances of signal_dict to signatures.SIGNAL_ID.validate() << think about this a little more than not at all
#       Ideally I'd like to keep the contents of each entity as close to the final output dict to reduce the amount
#       of computation that needs to take place
#       However, consider what will be the most clear to the user:
#       Keeping signal data in SignalID and Signal seem like a good idea, but do I do that for everything? Will that make
#       it less or more complex?
# TODO: documentation!

# Long term:
# TODO: defaults!
# TODO: "succinct" mode for to_dict(), integrate with better default management
# TODO: flipping and rotation of entities

from draftsman.classes.entitylike import EntityLike

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import InvalidEntityError
from draftsman.utils import aabb_to_dimensions

from schema import SchemaError
from typing import Any, Union, Callable


class Entity(EntityLike):
    def __init__(self, name, similar_entities, position = [0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        """
        """
        super(Entity, self).__init__()
        # Create a set of keywords that transfer in to_dict function
        # Since some things we want to keep internal without sending to to_dict
        # TODO: maybe make an Exportable class and use for Blueprint as well?
        self.exports = dict()
        # For user convinience, keep track of all the unused arguments, and 
        # issue a warning if the user provided one that was not used.
        # TODO: find a more elegant solution for this functionality
        self.unused_args = kwargs

        # Entities of the same type
        self.similar_entities = similar_entities

        # Name
        self.name = name
        self._add_export("name")

        # Entity type
        self._type = entities.raw[self.name]["type"]

        # ID (used in Blueprints) (do we want this?)
        self.id = None
        if "id" in kwargs:
            self.id = kwargs["id"]
            self.unused_args.pop("id")

        # Collision box (Internal)
        self._collision_box = entities.raw[self.name]["collision_box"].copy()

        # Tile Width and Height (Internal)
        self._tile_width, self._tile_height = aabb_to_dimensions(
            self.collision_box
        )
        if "tile_width" in entities.raw[self.name]:
            self._tile_width = entities.raw[self.name]["tile_width"]
        if "tile_height" in entities.raw[self.name]:
            self._tile_height = entities.raw[self.name]["tile_height"]

        # Hidden? (Internal)
        self.hidden = "hidden" in entities.raw[self.name]["flags"]

        # Position
        self.position = position
        self._add_export("position")

        # Entity tags
        self.tags = {}
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
            self.unused_args.pop("tags")
        self._add_export("tags", lambda x: x)

    # =========================================================================

    @property
    def name(self):
        # type: () -> str
        """
        The name of the entity. The name must be a Factorio ID string; Setting
        the name to anything else raises an `InvalidEntityID` error.
        """
        return self._name

    @name.setter
    def name(self, value):
        # type: (str) -> None
        if value in self.similar_entities:
            self._name = value
        else:
            raise InvalidEntityError("'{}' is not a valid name for this type"
                                     .format(value))
        

    # =========================================================================

    @property
    def type(self):
        # type: () -> str
        """
        Read Only
        """
        return self._type

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
    def position(self, position):
        # type: (Union[list, dict]) -> None
        # TODO: there has a better way to do this
        # position = signatures.POSITION.validate(position)
        # if isinstance(position, list):
        #     self.set_tile_position(position[0], position[1])
        # elif isinstance(position, dict): # pragma: no branch
        #     self.set_absolute_position(position["x"], position["y"])
        try:
            position = signatures.POSITION.validate(position) # TODO: remove
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid position format")
        try:
            self.set_absolute_position(position["x"], position["y"])
        except TypeError:
            self.set_tile_position(position[0], position[1])

    # =========================================================================

    @property
    def collision_box(self):
        # type: () -> list
        """
        Read Only
        """
        return self._collision_box

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        Read Only
        """
        return self._tile_width

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        Read Only
        """
        return self._tile_height

    # =========================================================================

    @property
    def tags(self):
        # type: () -> dict
        """
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        # type: (dict) -> None
        if tags is None:
            self._tags = None
        elif isinstance(tags, dict):
            self._tags = tags
        else:
            raise TypeError("Attribute 'tags' must be a dict")

    # =========================================================================

    def set_absolute_position(self, x, y):
        # type: (float, float) -> None
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self._position = signatures.ABS_POSITION.validate({"x": x, "y": y})
        grid_x = round(self._position["x"] - self.tile_width / 2.0)
        grid_y = round(self._position["y"] - self.tile_height / 2.0)
        self.tile_position = [grid_x, grid_y]

    def set_tile_position(self, x, y):
        # type: (int, int) -> None
        """
        Sets the grid position of the object, or the tile coordinates of the
        object. Calculates the absolute position based off of the dimensions of
        the entity. If a tile is multiple tiles in width or height, the grid
        coordinate is the top left-most tile of the entity.
        """
        self.tile_position = signatures.TILE_POSITION.validate([x, y])
        absolute_x = self.tile_position[0] + self.tile_width / 2.0
        absolute_y = self.tile_position[1] + self.tile_height / 2.0
        self._position = {"x": absolute_x, "y": absolute_y}

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the entity.
        """
        return [[self.collision_box[0][0] + self.position["x"],
                 self.collision_box[0][1] + self.position["y"]],
                [self.collision_box[1][0] + self.position["x"],
                 self.collision_box[1][1] + self.position["y"]]]

    def to_dict(self):
        # type: () -> dict
        """
        Converts the Entity to its JSON dict representation. The keys returned
        are determined by the contents of the `exports` dictionary and their
        function values.

        TODO: come up with a more generic method for inserting into blueprint
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

    # def export(self, blueprint):
    #     """
    #     Maybe something like this for a more generic method?
    #     """
    #     out = {}
    #     for name, funcs in self.exports.items():
    #         value = getattr(self, name)
    #         criterion = funcs[0]
    #         formatter = funcs[1]
    #         # Does the value match the criteria to be included?
    #         if criterion is None or criterion(value):
    #             if formatter is not None:
    #                 # Normalize key/value pair
    #                 k, v = formatter(name, value)
    #             else:
    #                 k, v = name, value
    #             out[k] = v

    #     blueprint["entities"].append(out)

    def _add_export(self, name, criterion = None, formatter = None):
        # type: (str, Callable, Callable) -> None
        """
        Adds an export key with a criteria function.

        We can't just convert the entire entity to a dict, because there are a
        number of keys (for technical or space reasons) that we dont want to
        add to the dictionary. Instead, we hold a dictionary of the keys we do
        want to add to the dictionary and add those if they're present in the
        Entity object.

        However, some items that are present in Entity might be initialized to
        `None` or otherwise redundant values, which would just take up space in 
        the output dict. Hence, we can also provide a criteria function that 
        takes a single argument, the value of the element in the `Entity`. If 
        the function is not present, or if the function is present and returns 
        `True`, then the key and its value are added to the output dict.
        """
        self.exports[name] = [criterion, formatter]

    def __repr__(self):
        # type: () -> str
        return "<{}>{}".format(self.__class__.__name__, str(self.to_dict()))