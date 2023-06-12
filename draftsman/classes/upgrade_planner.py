# upgrade_planner.py
# -*- encoding: utf-8 -*-

"""
.. code-block:: python

    {
        "upgrade_planner": {
            "item": "upgrade-planner", # The associated item with this structure
            "label": str, # A user given name for this upgrade planner
            "version": int, # The encoded version of Factorio this planner was created 
                            # with/designed for (64 bits)
            "settings": {
                "mappers": [ # List of dicts, each one a "mapper"
                    {
                        "from": { # The from entity/item. If this key is omitted, it appears blank in-game
                            "name": str, # The name of a valid replacable entity/item
                            "type": "entity" or "item" # Depending on name
                        },
                        "to": { # The to entity/item. If this key is omitted, it appears blank in-game
                            "name": str, # The name of a different, corresponding entity/item
                            "type": "entity" or "item" # Depending on name
                        },
                        "index": u64 # in range [1, max_mappers as defined in prototypes]
                    },
                    .. # Up to 24 mappers total for default upgrade planner
                ],
                "description": str, # A user given description for this upgrade planner
                "icons": [ # A set of signals to act as visual identification
                    {
                        "signal": {"name": str, "type": str}, # Name and type of signal
                        "index": int, # In range [1, 4], starting top-left and moving across and down
                    },
                    ... # Up to 4 icons total
                ]
            }
        }
    }
"""

from __future__ import unicode_literals

from draftsman import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.data import entities, items, modules
from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import (
    ItemLimitationWarning,
    ValueWarning,
    IndexWarning,
    DraftsmanWarning,
    RedundantOperationWarning,
    UnrecognizedElementWarning
)

import copy
import fastjsonschema
from schema import SchemaError
import six
from typing import Union, Sequence
import warnings


def check_valid_upgrade_pair(from_obj, to_obj):
    """
    Checks two :py:data:`MAPPING_ID` objects to see if it's possible for 
    ``from_obj`` to upgrade into ``to_obj``.

    :param from_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key.
    :param to_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key.

    :returns: A Warning object with the reason why the mapping would be invalid,
        or ``None`` if no reason could be found.
    """

    # If both from and to are the same, the game will allow it; but the GUI
    # prevents the user from doing it and it ends up being functionally useless,
    # so we warn the user since this is likely not intentional
    if from_obj["name"] == to_obj["name"]:
        return RedundantOperationWarning(
            False,
            "Mapping entity/item '{}' to itself has no effect".format(from_obj["name"]),
        )

    # Next we need to check if Draftsman even recognizes both from and to,
    # because if not then Draftsman cannot possibly expect to know whether the
    # upgrade pair is valid or not; hence, we early exit with a simple
    # "unrecognized entity/item" warning:
    # FIXME: technically this will only issue one warning if both are unrecognized
    # FIXME: technically this will only issue warnings if both to and from are defined,
    # so it probably makes sense to move this to inspect()
    if from_obj["name"] not in entities.raw and from_obj["name"] not in items.raw:
        return UnrecognizedElementWarning(
            "Unrecognized entity/item '{}'".format(from_obj["name"])
        )
    if to_obj["name"] not in entities.raw and to_obj["name"] not in items.raw:
        return UnrecognizedElementWarning(
            "Unrecognized entity/item '{}'".format(to_obj["name"])
        )

    # To quote Entity prototype documentation for the "next_upgrade" key:
    # > "This entity may not have 'not-upgradable' flag set and must be
    # > minable. This entity mining result must not contain item product
    # > with "hidden" flag set. Mining results with no item products are
    # > allowed. The entity may not be a Prototype/RollingStock. The
    # > upgrade target entity needs to have the same bounding box,
    # > collision mask, and fast replaceable group as this entity. The
    # > upgrade target entity must have least 1 item that builds it that
    # > isn't hidden.
    from_entity = entities.raw[from_obj["name"]]
    to_entity = entities.raw[to_obj["name"]]

    # from must be upgradable
    if "not-upgradable" in from_entity.get("flags", set()):
        return DraftsmanWarning("'{}' is not upgradable".format(from_obj["name"]))

    # from must be minable
    if not from_entity.get("minable", False):
        return DraftsmanWarning("'{}' is not minable".format(from_obj["name"]))

    # Mining results from the upgrade must not be hidden
    if "results" in from_entity["minable"]:
        mined_items = from_entity["minable"]["results"]
    else:
        mined_items = from_entity["minable"]["result"]
    # I assume that it means ALL of the items have to be not hidden
    for mined_item in mined_items:
        if "hidden" in items.raw[mined_item].get("flags", set()):
            return DraftsmanWarning(
                "Returned item '{}' when mining '{}' is hidden".format(
                    mined_item, from_obj["name"]
                ),
            )

    # Cannot upgrade rolling stock (train cars)
    if from_entity["type"] in {
        "locomotive",
        "cargo-wagon",
        "fluid-wagon",
        "artillery-wagon",
    }:
        return DraftsmanWarning(
            "Cannot upgrade '{}' because it is RollingStock".format(from_obj["name"]),
        )

    # Collision boxes must match (assuming None is valid)
    if from_entity.get("collision_box", None) != to_entity.get("collision_box", None):
        return DraftsmanWarning(
            "Cannot upgrade '{}' to '{}'; collision boxes differ".format(
                from_obj["name"], to_obj["name"]
            ),
        )

    # Collision masks must match (assuming None is valid)
    if from_entity.get("collision_mask", None) != to_entity.get("collision_mask", None):
        return DraftsmanWarning(
            "Cannot upgrade '{}' to '{}'; collision masks differ".format(
                from_obj["name"], to_obj["name"]
            ),
        )

    # Fast replacable groups must match (assuming None is valid)
    ffrg = from_entity.get("fast_replaceable_group", None)
    tfrg = to_entity.get("fast_replaceable_group", None)
    if ffrg != tfrg:
        return DraftsmanWarning(
            "Cannot upgrade '{}' to '{}'; fast replacable groups differ".format(
                from_obj["name"], to_obj["name"]
            ),
        )

    # Otherwise, we must conclude that the mapping makes sense
    return None

signal_schema = {
    "$id": "SIGNAL_DICT",
    "title": "Signal dict",
    "description": "JSON object that represents a signal. Used in the circuit network, but also used for blueprintable icons.",
    "type": "object",
    "properties": {
        "name": {
            "description": "Must be a name recognized by Factorio, or will error on import.",
            "type": "string"
        },
        "type": {
            "description": "Must be one of the following values, or will error on import.",
            "type": "string",
            "enum": ["item", "fluid", "virtual"]
        }
    },
    "required": ["name", "type"],
    "additionalProperties": False
}

mapper_schema = {
    "$id": "MAPPER_DICT",
    "title": "Mapper dict",
    "description": "JSON object that represents a mapper. Used in Upgrade Planners to describe their function.",
    "type": "object",
    "properties": {
        "name": {
            "description": "Must be a name recognized by Factorio, or will error on import.",
            "type": "string"
        },
        "type": {
            "description": "Must be one of the following values, or will error on import. Item refers to modules, entity refers to everything else (as far as I've investigated; modded objects might change this behavior, but I have yet to find out)",
            "type": "string",
            "enum": ["item", "entity"]
        }
    },
    "required": ["name", "type"],
    "additionalProperties": False
}

icons_schema = {
    "$id": "ICONS_ARRAY",
    "title": "Icons list",
    "description": "Format of the list of signals used to give blueprintable objects unique appearences. Only a maximum of 4 entries are allowed; indicies outside of the range [1, 4] will return 'Index out of bounds', and defining multiple icons that use the same index returns 'Icon already specified'.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "signal": {
                "description": "Which signal icon to use.",
                "$ref": "factorio-draftsman://SIGNAL_DICT"
            },
            "index": {
                "description": "What index to place the signal icon, 1-indexed.",
                "type": "integer",
                "minimum": 1,
                "maximum": 4
            }
        },
        "required": ["signal", "index"],
        "additionalProperties": False
    },
    "maxItems": 4
}

def _draftsman_uri_handler(item):
    mapping = {
        "factorio-draftsman://SIGNAL_DICT": signal_schema,
        "factorio-draftsman://MAPPER_DICT": mapper_schema,
        "factorio-draftsman://ICONS_ARRAY": icons_schema,
    }
    return mapping[item]

class UpgradePlanner(Blueprintable):
    """
    A :py:class:`.Blueprintable` used to upgrade and downgrade entities and
    items.
    """

    schema = {
        "title": "Upgrade Planner Format",
        "description": "The explicit format of a valid Upgrade Planner JSON dict.",
        "type": "object",
        "properties": {
            "upgrade_planner": {
                "description": "Root entry in the format.",
                "type": "object",
                "properties": {
                    "item": {
                        "description": "The associated item with this structure.",
                        "type": "string"
                    },
                    "label": {
                        "description": "A user given name for this upgrade planner",
                        "type": "string"
                    },
                    "version": {
                        "description": "The encoded version of Factorio this planner was created with/designed for.",
                        "type": "integer",
                        "minimum": 0,
                        "exclusiveMaximum": 2**64,
                    },
                    "settings": {
                        "description": "Information relating to mappings, as well as additional descriptors.",
                        "type": "object",
                        "properties": {
                            "description": {
                                "description": "A user given description for this upgrade planner. Don't ask me why this is in the settings object.",
                                "type": "string"
                            },
                            "icons": {
                                "description": "A set of signals to act as visual identification. Don't ask me why this is in the settings object.",
                                "$ref": "factorio-draftsman://ICONS_ARRAY"
                            },
                            "mappers": {
                                "description": "A list of mapping objects that describe from what entity to upgrade and what entity to upgrade to.",
                                "type": "array",
                                "items": {
                                    "description": "A single 'mapper' object.",
                                    "type": "object",
                                    "properties": {
                                        "from": { 
                                            "$ref": "factorio-draftsman://MAPPER_DICT" 
                                        },
                                        "to": { 
                                            "$ref": "factorio-draftsman://MAPPER_DICT" 
                                        },
                                        "index": {
                                            "description": "The location in the upgrade planner to display the mapping, 0-indexed. If the index is greater than or equal to the max mappers for this Upgrade Planner (24 by default) then such entries will be ignored when imported.",
                                            "type": "integer",
                                            "minimum": 0,
                                            "exclusiveMaximum": 2**64,
                                        }
                                    },
                                    "required": ["index"],
                                    "additionalProperties": False,
                                }
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "required": ["item"],
                "additionalProperties": False
            }
        },
        "required": ["upgrade_planner"],
        "additionalProperties": False
    }
    validator = fastjsonschema.compile(schema, handlers={"factorio-draftsman": _draftsman_uri_handler})

    @utils.reissue_warnings
    def __init__(self, upgrade_planner=None, unknown="error"):
        # type: (Union[str, dict], str) -> None
        """
        Constructs a new :py:class:`.UpgradePlanner`.

        :param upgrade_planner: Either a dictionary containing all the key
            attributes to set, or
        """
        super(UpgradePlanner, self).__init__(
            root_item="upgrade_planner",
            item="upgrade-planner",
            init_data=upgrade_planner,
            unknown=unknown,
        )

    @utils.reissue_warnings
    def setup(self, unknown="error", **kwargs):
        self._root = {}
        self._root["settings"] = {}

        self._root["item"] = "upgrade-planner"
        kwargs.pop("item", None)

        self.label = kwargs.pop("label", None)

        if "version" in kwargs:
            self.version = kwargs.pop("version")
        else:
            self.version = utils.encode_version(*__factorio_version_info__)

        settings = kwargs.pop("settings", None)
        if settings is not None:
            self.mappers = settings.pop("mappers", None)
            self.description = settings.pop("description", None)
            self.icons = settings.pop("icons", None)

        # Issue warnings for any keyword not recognized by UpgradePlanner
        for unused_arg in kwargs:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def description(self):
        # type: () -> str
        return self._root["settings"].get("description", None)

    @description.setter
    def description(self, value):
        # type: (str) -> None
        if value is None:
            self._root["settings"].pop("description", None)
        else:
            self._root["settings"]["description"] = value

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        return self._root["settings"].get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[Union[dict, str]]) -> None
        if value is None:
            try:
                self._root["settings"].pop("icons", None)
            except KeyError:
                pass
        else:
            try:
                self._root["settings"]["icons"] = signatures.ICONS.validate(
                    value
                )  # TODO: remove
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def mapper_count(self):
        # type: () -> int
        """
        The total number of unique mappings that this entity can have. Read only.

        :type: int
        """
        return items.raw["upgrade-planner"]["mapper_count"]

    # =========================================================================

    @property
    def mappers(self):
        # type: () -> list
        """
        The list of mappings of one entity or item type to the other entity or
        item type.

        :raises DataFormatError: If setting this attribute and any of the
            entries in the list do not match the format specified above.

        :getter: Gets the mappers dictionary, or ``None`` if not set.
        :setter: Sets the mappers dictionary, or deletes the dictionary if set
            to ``None``
        :type: ``[{"from": {...}, "to": {...}, "index": int}]``
        """
        return self._root["settings"].get("mappers", None)

    @mappers.setter
    def mappers(self, value):
        # type: (Union[list[dict], list[tuple]]) -> None
        if value is None:
            del self._root["settings"]["mappers"]
            return

        self._root["settings"]["mappers"] = value

        # self._root["settings"]["mappers"] = []
        # for i, mapper in enumerate(value):
        #     if isinstance(mapper, dict):
        #         self.set_mapping(
        #             mapper.get("from", None), mapper.get("to", None), mapper["index"]
        #         )
        #     elif isinstance(mapper, Sequence):
        #         self.set_mapping(mapper[0], mapper[1], i)
        #     else:
        #         raise DataFormatError(
        #             "{} cannot be resolved to a UpgradePlanner Mapping"
        #         )

    # =========================================================================

    @utils.reissue_warnings
    def set_mapping(self, from_obj, to_obj, index):
        # type: (Union[str, dict], Union[str, dict], int) -> None
        """
        Sets a single mapping in the :py:class:`.UpgradePlanner`. Setting both
        ``from_obj`` and ``to_obj`` to ``None`` will remove all mapping entries
        at ``index`` (if there is one or more at that index).

        :param from_obj: The :py:data:`.SIGNAL_ID` to convert entities/items
            from. Can be set to ``None`` which will leave it blank.
        :param to_obj: The :py:data:`.SIGNAL_ID` to convert entities/items to.
            Can be set to ``None`` which will leave it blank.
        :param index: The location in the upgrade planner's mappers list.
        """
        # Check types of all parameters (SIGNAL_ID, SIGNAL_ID, int)
        try:
            from_obj = signatures.MAPPING_ID_OR_NONE.validate(from_obj)
            to_obj = signatures.MAPPING_ID_OR_NONE.validate(to_obj)
            index = signatures.INTEGER.validate(index)
        except SchemaError as e:
            six.raise_from(DataFormatError, e)

        if self.mappers is None:
            self.mappers = []

        # TODO: delete if None, None, int

        new_mapping = {"index": index}
        # Both 'from' and 'to' can be None and end up blank
        if from_obj is not None:
            new_mapping["from"] = from_obj
        if to_obj is not None:
            new_mapping["to"] = to_obj
        # Idiot check to make sure we get no exact duplicates
        if new_mapping not in self.mappers:
            self.mappers.append(new_mapping)

    def remove_mapping(self, from_obj, to_obj, index=None):
        """
        Removes an upgrade mapping occurence of an upgrade mapping. If ``index``
        is specified, it will attempt to remove that specific mapping from that
        specific index, otherwise it will search for the first occurence of a
        matching mapping. No action is performed if no mapping matches the input
        arguments.

        :param from_obj: The :py:data:`.SIGNAL_ID` to to convert entities/items
            from.
        :param to_obj: The :py:data:`.SIGNAL_ID` to convert entities/items to.
        :param index: The index of the mapping in the mapper to search.
        """
        try:
            from_obj = signatures.SIGNAL_ID_OR_NONE.validate(from_obj)
            to_obj = signatures.SIGNAL_ID_OR_NONE.validate(to_obj)
            index = signatures.INTEGER_OR_NONE.validate(index)
        except SchemaError as e:
            six.raise_from(DataFormatError, e)

        if index is None:
            # Remove the first occurence of the mapping, if there are multiple
            for i, mapping in enumerate(self.mappers):
                if mapping["from"] == from_obj and mapping["to"] == to_obj:
                    self.mappers.pop(i)
        else:
            mapper = {"from": from_obj, "to": to_obj, "index": index}
            try:
                self.mappers.remove(mapper)
            except ValueError:
                pass

    def validate(self):
        # type: () -> None
        # TODO
        # if self.is_valid:
        #     return

        result = self.__class__.validator({self._root_item: self._root})
        self._root = result[self._root_item]

        # TODO
        # self._is_valid = True

    def inspect(self):
        # type: () -> tuple(list[Exception], list[Warning])
        error_list = []
        warn_list = []
        # error_list, warn_list = super(Blueprintable, self).inspect() # TODO: implement

        # Keep track to see if multiple entries exist with the same index
        occupied_indices = {}

        # By nature of necessity, we must ensure that all members of upgrade 
        # planner are in a correct and known format, so we must call:
        try:
            self.validate()
        except fastjsonschema.JsonSchemaException as e:
            error_list.append(DataFormatError(e.args[0]))
            return (error_list, warn_list)

        # Check each mappers
        for mapper in self.mappers:
            # We assert that index must exist in each mapper, but "from" and "to"
            # may be omitted
            if "from" in mapper and "to" in mapper:
                # Ensure that "from" and "to" are a valid pair
                reason = check_valid_upgrade_pair(mapper["from"], mapper["to"])
                if reason is not None:
                    warn_list.append(reason)

            # If the index is not a u64, then that will fail to import
            if not 0 <= mapper["index"] < 2**64:
                error_list.append(
                    IndexError(
                        "'index' ({}) for mapping '{}' to '{}' must be a u64 in range [0, 2**64)".format(
                            mapper["index"], mapper["from"], mapper["to"]
                        )
                    )
                )

            # If the index is greater than mapper_count, then the mapping will
            # be redundant
            if not mapper["index"] < self.mapper_count:
                warn_list.append(
                    IndexWarning(
                        "'index' ({}) for mapping '{}' to '{}' must be in range [0, {}) or else it will have no effect".format(
                            mapper["index"],
                            mapper["from"],
                            mapper["to"],
                            self.mapper_count,
                        )
                    )
                )

            # Keep track of entries that occupy the same index (only the last
            # mapping is used)
            if mapper["index"] in occupied_indices:
                occupied_indices[mapper["index"]]["count"] += 1
                occupied_indices[mapper["index"]]["final"] = mapper
            else:
                occupied_indices[mapper["index"]] = {"count": 1, "final": mapper}

        # Issue warnings if multiple mappers occupy the same index
        for spot in occupied_indices:
            entry = occupied_indices[spot]
            if entry["count"] > 1:
                warn_list.append(
                    IndexWarning(  # TODO: more specific (maybe OverlappingIndexWarning?)
                        "Mapping at index {} was overwritten {} times; final mapping is '{}' to '{}'".format(
                            entry["mapping"]["index"],
                            entry["count"],
                            entry["mapping"]["to"],
                            entry["mapping"]["from"],
                        )
                    )
                )

        return (error_list, warn_list)

    def to_dict(self):
        # type: () -> dict

        # Ensure that we're in a known state
        # self.validate()

        # Create a copy so we don't change the original any further
        out_dict = copy.deepcopy(self._root)

        # Prune excess values
        # (No chance of KeyError because 'settings' should always be a key until 
        # we export)
        # TODO: integrate this into generic interface like I did with Entity
        if out_dict["settings"] == {}:
            del out_dict["settings"]

        return {"upgrade_planner": out_dict}
