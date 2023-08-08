# upgrade_planner.py

"""
.. code-block:: python

    >>> from draftsman.blueprintable import UpgradePlanner
    >>> UpgradePlanner.Format.schema_json(indent=4)
"""

from __future__ import unicode_literals

from draftsman import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import ValidationResult
from draftsman.data import entities, items, modules
from draftsman.error import DataFormatError
from draftsman.signatures import Icons, Mappers, Mapper, mapper_dict 
from draftsman import utils
from draftsman.warning import (
    IndexWarning,
    DraftsmanWarning,
    RedundantOperationWarning,
    UnrecognizedElementWarning,
)
from functools import cached_property

import bisect
import copy
from pydantic import BaseModel, Field, field_validator, ConfigDict
from schema import Schema, Optional, SchemaError
import six
from typing import Union, Sequence, Literal
import warnings


def check_valid_upgrade_pair(
    from_obj: dict | None, to_obj: dict | None
) -> list[Warning]:
    """
    Checks two :py:data:`MAPPING_ID` objects to see if it's possible for
    ``from_obj`` to upgrade into ``to_obj``.

    :param from_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key, or
        ``None`` if that entry was null.
    :param to_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key , or
        ``None`` if that entry was null.

    :returns: A list of one or more Warning objects containing the reason why
        the mapping would be invalid, or ``None`` if no reason could be deduced.
    """

    # First we need to check if Draftsman even recognizes both from and to,
    # because if not then Draftsman cannot possibly expect to know whether the
    # upgrade pair is valid or not; hence, we early exit with a simple
    # "unrecognized entity/item" warning:
    unrecognized = []
    if (
        from_obj is not None
        and from_obj["name"] not in entities.raw
        and from_obj["name"] not in items.raw
    ):
        unrecognized.append(
            UnrecognizedElementWarning(
                "Unrecognized entity/item '{}'".format(from_obj["name"])
            )
        )
    if (
        to_obj is not None
        and to_obj["name"] not in entities.raw
        and to_obj["name"] not in items.raw
    ):
        unrecognized.append(
            UnrecognizedElementWarning(
                "Unrecognized entity/item '{}'".format(to_obj["name"])
            )
        )
    if unrecognized:
        return unrecognized

    # If one (or both) of from and to are empty, then there's also no reason to
    # check if a mapping between them is valid because there's simply not
    # enough information
    if from_obj is None or to_obj is None:
        return None

    # If both from and to are the same, the game will allow it; but the GUI
    # prevents the user from doing it and it ends up being functionally useless,
    # so we warn the user since this is likely not intentional
    if from_obj == to_obj:
        return [
            RedundantOperationWarning(
                "Mapping entity/item '{}' to itself has no effect".format(
                    from_obj["name"]
                )
            )
        ]

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
        return [DraftsmanWarning("'{}' is not upgradable".format(from_obj["name"]))]

    # from must be minable
    if not from_entity.get("minable", False):
        return [DraftsmanWarning("'{}' is not minable".format(from_obj["name"]))]

    # Mining results from the upgrade must not be hidden
    if "results" in from_entity["minable"]:
        mined_items = [r["name"] for r in from_entity["minable"]["results"]]
    else:
        mined_items = [from_entity["minable"]["result"]]
    # I assume that it means ALL of the items have to be not hidden
    for mined_item in mined_items:
        if "hidden" in items.raw[mined_item].get("flags", set()):
            return [
                DraftsmanWarning(
                    "Returned item '{}' when upgrading '{}' is hidden".format(
                        mined_item, from_obj["name"]
                    ),
                )
            ]

    # Cannot upgrade rolling stock (train cars)
    if from_entity["type"] in {
        "locomotive",
        "cargo-wagon",
        "fluid-wagon",
        "artillery-wagon",
    }:
        return [
            DraftsmanWarning(
                "Cannot upgrade '{}' because it is RollingStock".format(
                    from_obj["name"]
                ),
            )
        ]

    # Collision boxes must match (assuming None is valid)
    if from_entity.get("collision_box", None) != to_entity.get("collision_box", None):
        return [
            DraftsmanWarning(
                "Cannot upgrade '{}' to '{}'; collision boxes differ".format(
                    from_obj["name"], to_obj["name"]
                ),
            )
        ]

    # Collision masks must match (assuming None is valid)
    if from_entity.get("collision_mask", None) != to_entity.get("collision_mask", None):
        return [
            DraftsmanWarning(
                "Cannot upgrade '{}' to '{}'; collision masks differ".format(
                    from_obj["name"], to_obj["name"]
                ),
            )
        ]

    # Fast replacable groups must match (assuming None is valid)
    ffrg = from_entity.get("fast_replaceable_group", None)
    tfrg = to_entity.get("fast_replaceable_group", None)
    if ffrg != tfrg:
        return [
            DraftsmanWarning(
                "Cannot upgrade '{}' to '{}'; fast replacable groups differ".format(
                    from_obj["name"], to_obj["name"]
                ),
            )
        ]

    # Otherwise, we must conclude that the mapping makes sense
    return None


class UpgradePlannerModel(BaseModel):
    """
    TODO
    Upgrade planner object schema.
    """

    item: Literal["upgrade-planner"] = "upgrade-planner"
    label: str | None = None
    version: int | None = Field(None, ge=0, lt=2**64)

    class Settings(BaseModel):
        """
        TODO
        """

        description: str | None = None
        icons: Icons | None = None
        mappers: Mappers | None = None

    settings: Settings | None = Settings()

    @field_validator("item")
    def correct_item(cls, v):
        assert v == "upgrade-planner"
        return v


class UpgradePlanner(Blueprintable):
    """
    A :py:class:`.Blueprintable` used to upgrade and downgrade entities and
    items.
    """

    class Format(BaseModel):
        """
        The full description of UpgradePlanner's formal schema.
        """
        upgrade_planner: UpgradePlannerModel = UpgradePlannerModel()

        model_config = ConfigDict(title="UpgradePlanner", extra="forbid")

    # =========================================================================

    @utils.reissue_warnings
    def __init__(self, upgrade_planner=None, unknown="error"):
        # type: (Union[str, dict], str) -> None
        """
        Constructs a new :py:class:`.UpgradePlanner`.

        :param upgrade_planner: Either a dictionary containing all the key
            attributes to set, or a blueprint string to import.
        """
        super(UpgradePlanner, self).__init__(
            format=UpgradePlannerModel,
            root_item="upgrade_planner",
            item="upgrade-planner",
            init_data=upgrade_planner,
            unknown=unknown,
        )

    @utils.reissue_warnings
    def setup(self, unknown="error", **kwargs):
        # _root = {}
        # _root["settings"] = {}

        # _root["item"] = "upgrade-planner"
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
        return self._root.settings.get("description", None)

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
            self._root["settings"].pop("icons", None)
        else:
            self._root["settings"]["icons"] = value

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
        # type: () -> list[dict]
        """
        The list of mappings of one entity or item type to the other entity or
        item type.

        Using :py:meth:`.set_mapping()` will attempt to keep this list sorted
        by each mapping's internal ``"index"``, but outside of this function
        this  behavior is not required or enforced.

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
            self._root["settings"].pop("mappers", None)
        else:
            self._root["settings"]["mappers"] = value

    # =========================================================================

    @utils.reissue_warnings
    def set_mapping(self, from_obj, to_obj, index):
        # type: (Union[str, dict], Union[str, dict], int) -> None
        """
        Sets a single mapping in the :py:class:`.UpgradePlanner`. Setting
        multiple mappers at the same index overwrites the entry at that index
        with the last set value. Both ``from_obj`` and ``to_obj`` can be set to
        ``None`` which will create an unset mapping (and the resulting spot on
        the in-game GUI will be blank).

        This function will also attempt to keep the list sorted by each mapper's
        ``index`` key. This behavior is not enforced anywhere else, and if the
        :py:attr:`.mappers` list is ever made unsorted, calling this function
        does not resort said list and does not guarantee a correct sorted result.

        :param from_obj: The :py:data:`.MAPPING_ID` to convert entities/items
            from. Can be set to ``None`` which will leave it blank.
        :param to_obj: The :py:data:`.MAPPING_ID` to convert entities/items to.
            Can be set to ``None`` which will leave it blank.
        :param index: The location in the upgrade planner's mappers list.
        """
        from_obj = mapper_dict(from_obj)
        to_obj = mapper_dict(to_obj)
        index = int(index)

        if self.mappers is None:
            self.mappers = []

        new_mapping = {"index": index}
        # Both 'from' and 'to' can be None and end up blank
        if from_obj is not None:
            new_mapping["from"] = from_obj
        if to_obj is not None:
            new_mapping["to"] = to_obj

        # Iterate over indexes to see where we should place the new mapping
        for i, current_mapping in enumerate(self.mappers):
            # If we find an exact index match, replace it
            if current_mapping["index"] == index:
                self.mappers[i] = new_mapping
                return
        # Otherwise, insert it sorted by index
        # TODO: make backwards compatible
        bisect.insort(self.mappers, new_mapping, key=lambda x: x["index"])

    def remove_mapping(self, from_obj, to_obj, index=None):
        # type: (Union[str, dict], Union[str, dict], int) -> None
        """
        Removes a specified upgrade planner mapping. If ``index`` is not
        specified, the function searches for the first occurrence where both
        ``from_obj`` and ``to_obj`` match. If ``index`` is also specified, the
        algorithm will try to remove the first occurrence where all 3 criteria
        match.

        .. NOTE::

            ``index`` in this case refers to the index of the mapper in the
            **UpgradePlanner's GUI**, *not* it's position in the
            :py:attr:`.mappers` list; these two numbers are potentially disjunct.
            For example, `upgrade_planner.mappers[0]["index"]` is not
            necessarily ``0``.

        :raises ValueError: If the specified mapping does not currently exist
            in the :py:attr:`.mappers` list.

        :param from_obj: The :py:data:`.MAPPING_ID` to to convert entities/items
            from.
        :param to_obj: The :py:data:`.MAPPING_ID` to convert entities/items to.
        :param index: The index of the mapping in the mapper to search.
        """
        from_obj = mapper_dict(from_obj)
        to_obj = mapper_dict(to_obj)
        index = int(index) if index is not None else None

        if index is None:
            # Remove the first occurence of the mapping, if there are multiple
            for i, mapping in enumerate(self.mappers):
                if (
                    mapping.get("from", None) == from_obj
                    and mapping.get("to", None) == to_obj
                ):
                    self.mappers.pop(i)
                    return
            # Otherwise, raise ValueError if we didn't find a match
            raise ValueError(
                "Unable to find mapper from '{}' to '{}'".format(from_obj, to_obj)
            )
        else:
            mapper = {"from": from_obj, "to": to_obj, "index": index}
            self.mappers.remove(mapper)

    def pop_mapping(self, index):
        # type: (int) -> Mapper
        """
        Removes a mapping at a specific mapper index. Note that this is not the
        position of the mapper in the :py:attr:`.mappers` list; it is the value
        if ``"index"`` key associated with one or more mappers. If there are
        multiple mapper objects that share the same index, then the only the
        first one is removed.

        :raises ValueError: If no matching mappers could be found that have a
            matching index.

        :param index: The index of the mapping in the mapper to search.
        """
        # TODO: maybe make index optional so that `UpgradePlaner.pop_mapping()`
        # pops the mapper with the highest "index" value?
        # TODO: should there be a second argument to supply a default similar
        # to how `pop()` works generally?

        # Simple search and pop
        for i, mapping in enumerate(self.mappers):
            if mapping["index"] == index:
                return self.mappers.pop(i)

        raise ValueError("Unable to find mapper with index '{}'".format(index))

    def validate(self):
        # type: () -> None
        if self.is_valid:
            return

        # TODO: wrap with DataFormatError or similar
        self._root = UpgradePlannerModel.model_validate(self._root).model_dump(
            by_alias=True, exclude_none=True
        )

        super().validate()

    def inspect(self):
        # type: () -> ValidationResult
        result = super().inspect()

        # By nature of necessity, we must ensure that all members of upgrade
        # planner are in a correct and known format, so we must call:
        try:
            self.validate()
        except Exception as e:
            # If validation fails, it's in a format that we do not expect; and
            # therefore unreasonable for us to assume that we can continue
            # checking for errors relating to that non-existent format.
            # Therefore, we add the errors to the error list and early exit
            # TODO: figure out the proper way to reraise
            result.error_list.append(DataFormatError(str(e)))
            return result

        # Keep track to see if multiple entries exist with the same index
        occupied_indices = {}
        # Check each mapper
        for mapper in self.mappers:
            # Ensure that "from" and "to" are a valid pair
            # We assert that index must exist in each mapper, but both "from"
            # and "to" may be omitted
            reasons = check_valid_upgrade_pair(
                mapper.get("from", None), mapper.get("to", None)
            )
            if reasons is not None:
                result.warning_list.extend(reasons)

            # If the index is greater than mapper_count, then the mapping will
            # be redundant
            if not mapper["index"] < self.mapper_count:
                result.warning_list.append(
                    IndexWarning(
                        "'index' ({}) for mapping '{}' to '{}' must be in range [0, {}) or else it will have no effect".format(
                            mapper["index"],
                            mapper["from"]["name"],
                            mapper["to"]["name"],
                            self.mapper_count,
                        )
                    )
                )

            # Keep track of entries that occupy the same index (only the last
            # mapping is used)
            if mapper["index"] in occupied_indices:
                occupied_indices[mapper["index"]]["count"] += 1
                occupied_indices[mapper["index"]]["mapper"] = mapper
            else:
                occupied_indices[mapper["index"]] = {"count": 0, "mapper": mapper}

        # Issue warnings if multiple mappers occupy the same index
        for spot in occupied_indices:
            entry = occupied_indices[spot]
            if entry["count"] > 0:
                result.warning_list.append(
                    IndexWarning(
                        "Mapping at index {} was overwritten {} time(s); final mapping is '{}' to '{}'".format(
                            spot,
                            entry["count"],
                            entry["mapper"].get("from", {"name": None})["name"],
                            entry["mapper"].get("to", {"name": None})["name"],
                        )
                    )
                )

        return result

    def to_dict(self):
        # type: () -> dict
        out_dict = self.__class__.Format.model_construct(  # Performs no validation(!)
            _recursive=True,
            upgrade_planner=self._root
        )
        print("\tout_dict:", out_dict)
        out_dict = out_dict.model_dump(
            by_alias=True,  # Some attributes are reserved words (type, from,
                            # etc.); this resolves that issue
            exclude_none=True,  # Trim if values are None
            exclude_defaults=True,  # Trim if values are defaults
        )

        # TODO: FIXME; this is scuffed, ideally it would be part of the last
        # step, but there are some peculiarities with pydantic
        if not out_dict[self._root_item].get("settings", True):
            del out_dict[self._root_item]["settings"]

        return out_dict
