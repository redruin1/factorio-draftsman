# entity.py
# -*- encoding: utf-8 -*-

# TODO: make sure that all functions that modify the entity preserve the
#       entity's contents when they throw an error (this is done for the most
#       part, though I'm sure there are corner cases)
# TODO: documentation!

# Long term:
# TODO: defaults!
# TODO: "succinct" mode for to_dict(), integrate with better default management
# TODO: flipping and rotation of entities

from __future__ import unicode_literals

from draftsman.classes.entitylike import EntityLike

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import InvalidEntityError, DraftsmanError
from draftsman.utils import aabb_to_dimensions

import math
from schema import SchemaError
from typing import Any, Union, Callable
import six


class Entity(EntityLike):
    def __init__(self, name, similar_entities, tile_position=[0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        """ """
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
        if name not in self.similar_entities:
            raise InvalidEntityError(
                "'{}' is not a valid name for this {}".format(
                    name, self.__class__.__name__
                )
            )
        self._name = name
        self._add_export("name")

        # Entity type
        self._type = entities.raw[self.name]["type"]

        # ID (used in Blueprints and Groups)
        self.id = None
        if "id" in kwargs:
            self.id = kwargs["id"]
            self.unused_args.pop("id")

        # Collision box (Internal)
        self._collision_box = entities.raw[self.name]["collision_box"][:]  # copy

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
        self._tile_width, self._tile_height = aabb_to_dimensions(self._collision_box)
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
        self._add_export("position")

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
        Read Only
        The name of the entity. The name must be a Factorio ID string; Setting
        the name to anything else raises an `InvalidEntityID` error.
        """
        return self._name

    # @name.setter
    # def name(self, value):
    #     # type: (str) -> None
    #     if value in self.similar_entities:
    #         if self.blueprint:
    #             raise DraftsmanError(
    #                 "Cannot change name of entity while in a Blueprint"
    #             )
    #         self._name = value
    #     else:
    #         raise InvalidEntityError("'{}' is not a valid name for this type"
    #                                  .format(value))

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
        """ """
        return self._id

    @id.setter
    def id(self, value):
        # type: (str) -> None
        if value is None or isinstance(value, six.string_types):
            value = value if value is None else six.text_type(value)
            old_id = getattr(self, "_id", None)
            self._id = value
            if self.blueprint:
                self.blueprint.entities.remove_key(old_id)
                self.blueprint.entities.set_key(value, self)
        else:
            raise TypeError("'id' must be a str or None")

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        The position of the entity.

        Positions of most entities are located
        at their center, which can either be in the middle of a tile or it's
        transition, depending on the entities `tile_width` and `tile_height`.
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        if self.blueprint:
            raise DraftsmanError(
                "Cannot change position of entity while it's inside a Blueprint"
            )

        try:
            self._position = {"x": float(value["x"]), "y": float(value["y"])}
        except TypeError:
            self._position = {"x": float(value[0]), "y": float(value[1])}

        grid_x = round(self._position["x"] - self._tile_width / 2.0)
        grid_y = round(self._position["y"] - self._tile_height / 2.0)
        self._tile_position = {"x": grid_x, "y": grid_y}

    # =========================================================================

    @property
    def tile_position(self):
        # type: () -> dict
        """
        The tile-position of the Entity.

        `tile_position` is the position according to the LuaSurface tile grid,
        and is represented as integers
        """
        return self._tile_position

    @tile_position.setter
    def tile_position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        if self.blueprint:
            raise DraftsmanError(
                "Cannot change position of entity while it's inside a Blueprint"
            )

        try:
            self._tile_position = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self._tile_position = {"x": math.floor(value[0]), "y": math.floor(value[1])}

        absolute_x = self._tile_position["x"] + self._tile_width / 2.0
        absolute_y = self._tile_position["y"] + self._tile_height / 2.0
        self._position = {"x": absolute_x, "y": absolute_y}

        # if self.blueprint:
        #     self.blueprint.recalculate_area()

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
    def collision_mask(self):
        # type: () -> set
        """
        Read only
        """
        return self._collision_mask

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
    def hidden(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._hidden

    # =========================================================================

    @property
    def tags(self):
        # type: () -> dict
        """ """
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

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the entity.
        """
        return [
            [
                self.collision_box[0][0] + self.position["x"],
                self.collision_box[0][1] + self.position["y"],
            ],
            [
                self.collision_box[1][0] + self.position["x"],
                self.collision_box[1][1] + self.position["y"],
            ],
        ]

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

    def _add_export(self, name, criterion=None, formatter=None):
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

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        return "<{}>{}".format(self.__class__.__name__, str(self.to_dict()))
