# upgrade_planner.py

"""
.. code-block:: python

    >>> from draftsman.blueprintable import UpgradePlanner
    >>> UpgradePlanner.Format.schema_json(indent=4)
"""

from draftsman import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import ValidationResult, attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.data import entities, items
from draftsman.error import DataFormatError
from draftsman.signatures import (
    DraftsmanBaseModel,
    Icon,
    Mapper,
    MapperID,
    mapper_dict,
    uint8,
    uint16,
    uint64,
)
from draftsman.utils import encode_version, reissue_warnings
from draftsman.warning import (
    IndexWarning,
    NoEffectWarning,
    UnknownElementWarning,
    UpgradeProhibitedWarning,
)

import bisect
from pydantic import ConfigDict, Field, ValidationInfo, field_validator, model_validator
from typing import Any, Literal, Optional, Sequence, Union


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
            UnknownElementWarning(
                "Unrecognized entity/item '{}'".format(from_obj["name"])
            )
        )
    if (
        to_obj is not None
        and to_obj["name"] not in entities.raw
        and to_obj["name"] not in items.raw
    ):
        unrecognized.append(
            UnknownElementWarning(
                "Unrecognized entity/item '{}'".format(to_obj["name"])
            )
        )
    if unrecognized:
        return unrecognized

    # If one (or both) of from and to are empty, then there's also no reason to
    # check if a mapping between them is valid because there's just simply not
    # enough information
    if from_obj is None or to_obj is None:
        return None

    # If both from and to are the same, the game will allow it; but the GUI
    # prevents the user from doing it and it ends up being functionally useless,
    # so we warn the user since this is likely not intentional
    if from_obj == to_obj:
        return [
            NoEffectWarning(
                "Mapping entity/item '{}' to itself has no effect".format(
                    from_obj["name"]
                )
            )
        ]

    # The types of both need to match in order to make sense
    if from_obj["type"] != to_obj["type"]:
        return [
            UpgradeProhibitedWarning(
                "'{}' is an {} but '{}' is an {}".format(
                    from_obj["name"],
                    from_obj["type"],
                    to_obj["name"],
                    to_obj["type"],
                )
            )
        ]

    # TODO: currently we don't check for item mapping correctness
    # For now we just ignore it and early exit
    if from_obj["type"] == "item" and to_obj["type"] == "item":
        return None

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
        return [
            UpgradeProhibitedWarning("'{}' is not upgradable".format(from_obj["name"]))
        ]

    # from must be minable
    if not from_entity.get("minable", False):
        return [
            UpgradeProhibitedWarning("'{}' is not minable".format(from_obj["name"]))
        ]

    # Mining results from the upgrade must not be hidden
    if "results" in from_entity["minable"]:
        mined_items = [r["name"] for r in from_entity["minable"]["results"]]
    else:
        mined_items = [from_entity["minable"]["result"]]
    # I assume that it means ALL of the items have to be not hidden
    for mined_item in mined_items:
        if "hidden" in items.raw[mined_item].get("flags", set()):
            return [
                UpgradeProhibitedWarning(
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
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' because it is RollingStock".format(
                    from_obj["name"]
                ),
            )
        ]

    # Collision boxes must match (assuming None is valid)
    if from_entity.get("collision_box", None) != to_entity.get("collision_box", None):
        return [
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' to '{}'; collision boxes differ".format(
                    from_obj["name"], to_obj["name"]
                ),
            )
        ]

    # Collision masks must match (assuming None is valid)
    if from_entity.get("collision_mask", None) != to_entity.get("collision_mask", None):
        return [
            UpgradeProhibitedWarning(
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
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' to '{}'; fast replacable groups differ".format(
                    from_obj["name"], to_obj["name"]
                ),
            )
        ]

    # Otherwise, we must conclude that the mapping makes sense
    return None


class UpgradePlanner(Blueprintable):
    """
    A :py:class:`.Blueprintable` used to upgrade and downgrade entities and
    items.
    """

    # =========================================================================
    # Format
    # =========================================================================

    class Format(DraftsmanBaseModel):
        """
        The full description of UpgradePlanner's formal schema.
        """

        class UpgradePlannerObject(DraftsmanBaseModel):
            item: Literal["upgrade-planner"] = Field(
                ...,
                description="""
                The item that this UpgradeItem object is associated with. Always
                equivalent to 'upgrade-planner'.
                """,
            )
            label: Optional[str] = Field(
                None,
                description="""
                A string title for this UpgradePlanner.
                """,
            )
            version: Optional[uint64] = Field(
                None,
                description="""
                What version of Factorio this UpgradePlanner was made 
                in/intended for. Specified as 4 unsigned 16-bit numbers combined, 
                representing the major version, the minor version, the patch 
                number, and the internal development version respectively. The 
                most significant digits correspond to the major version, and the 
                least to the development number. 
                """,
            )

            class Settings(DraftsmanBaseModel):
                """
                Contains information about the UpgradePlanner, as well as what
                entities it maps to and from.
                """

                description: Optional[str] = Field(
                    None,
                    description="""
                    A string description given to this UpgradePlanner.""",
                )
                icons: Optional[list[Icon]] = Field(
                    None,
                    description="""
                    A set of signal pictures to associate with this 
                    UpgradePlanner.
                    """,
                )
                mappers: Optional[list[Mapper]] = Field(
                    None,
                    description="""
                    The set of mappings from one item/entity to another.
                    """,
                )

                @field_validator("icons", mode="before")
                @classmethod
                def normalize_icons(cls, value: Any):
                    if isinstance(value, Sequence):
                        result = [None] * len(value)
                        for i, signal in enumerate(value):
                            if isinstance(signal, str):
                                result[i] = {"index": i + 1, "signal": signal}
                            else:
                                result[i] = signal
                        return result
                    else:
                        return value

                @field_validator("mappers", mode="before")
                @classmethod
                def normalize_mappers(cls, value: Any):
                    if isinstance(value, Sequence):
                        result = []
                        for i, mapper in enumerate(value):
                            if isinstance(mapper, Sequence):
                                result.append({"index": i})
                                if mapper[0]:
                                    result[i]["from"] = mapper[0]
                                if mapper[1]:
                                    result[i]["to"] = mapper[1]
                            else:
                                result.append(mapper)
                        return result
                    else:
                        return value

                @model_validator(mode="after")
                def ensure_mappers_valid(self, info: ValidationInfo):
                    if not info.context or self.mappers is None:
                        return self
                    elif info.context["mode"] <= ValidationMode.MINIMUM:
                        return self

                    warning_list: list = info.context["warning_list"]
                    upgrade_planner: UpgradePlanner = info.context["object"]

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
                            warning_list.extend(reasons)

                        # If the index is greater than mapper_count, then the mapping will
                        # be redundant
                        if not mapper["index"] < upgrade_planner.mapper_count:
                            warning_list.append(
                                IndexWarning(
                                    "'index' ({}) for mapping '{}' to '{}' must be in range [0, {}) or else it will have no effect".format(
                                        mapper["index"],
                                        mapper["from"]["name"],
                                        mapper["to"]["name"],
                                        upgrade_planner.mapper_count,
                                    )
                                )
                            )

                        # Keep track of entries that occupy the same index (only the last
                        # mapping is used)
                        if mapper["index"] in occupied_indices:
                            occupied_indices[mapper["index"]]["count"] += 1
                            occupied_indices[mapper["index"]]["mapper"] = mapper
                        else:
                            occupied_indices[mapper["index"]] = {
                                "count": 0,
                                "mapper": mapper,
                            }

                    # Issue warnings if multiple mappers occupy the same index
                    for spot in occupied_indices:
                        entry = occupied_indices[spot]
                        if entry["count"] > 0:
                            from_name = entry["mapper"].get("from", None)
                            from_name = (
                                from_name["name"]
                                if from_name is not None
                                else from_name
                            )
                            to_name = entry["mapper"].get("to", None)
                            to_name = (
                                to_name["name"] if to_name is not None else to_name
                            )
                            warning_list.append(
                                IndexWarning(
                                    "Mapping at index {} was overwritten {} time(s); final mapping is '{}' to '{}'".format(
                                        spot,
                                        entry["count"],
                                        from_name,
                                        to_name,
                                    )
                                )
                            )

                    return self

            settings: Optional[Settings] = Settings()

            @field_validator("version", mode="before")
            @classmethod
            def normalize_to_int(cls, value: Any):
                if isinstance(value, Sequence):
                    return encode_version(*value)
                return value

        upgrade_planner: UpgradePlannerObject
        index: Optional[uint16] = Field(
            None,
            description="""
            The index of the blueprint inside a parent BlueprintBook's blueprint
            list. Only meaningful when this object is inside a BlueprintBook.
            """,
        )

        model_config = ConfigDict(title="UpgradePlanner")

    # =========================================================================
    # Constructors
    # =========================================================================

    @reissue_warnings
    def __init__(
        self,
        upgrade_planner: Union[str, dict, None] = None,
        index: Optional[uint16] = None,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
        """
        Constructs a new :py:class:`.UpgradePlanner`.

        :param upgrade_planner: Either a dictionary containing all the key
            attributes to set, or a blueprint string to import.
        :param index: The index of this blueprintable object in a parent
            BlueprintBook. Only makes sense if this blueprintable actually
            exists inside of a BlueprintBook; If omitted, Draftsman will
            generate this value from the index of this blueprintable in the
            parent BlueprintBook's :py:attr:`.blueprints` list.
        :param validate: Whether or not to validate this object after
            construction, and how strict to be when doing so.
        :param validate_assignmene: Whether or not to validate setting the
            attributes of this object, and how strict to be when doing so.
        """
        self._root: __class__.Format

        super().__init__(
            root_item="upgrade_planner",
            root_format=UpgradePlanner.Format.UpgradePlannerObject,
            item="upgrade-planner",
            init_data=upgrade_planner,
            index=index,
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    @reissue_warnings
    def setup(
        self,
        label: str = None,
        version: uint64 = __factorio_version_info__,
        settings: Format.UpgradePlannerObject.Settings = Format.UpgradePlannerObject.Settings(),
        index: Optional[uint16] = None,
        if_unknown: str = "error",  # TODO: enum
        **kwargs
    ):
        kwargs.pop("item", None)

        self.label = label
        self.version = version
        self._root[self._root_item]["settings"] = settings

        # self._root[self._root_item]["settings"] = {}
        # input_settings = kwargs.pop("settings", None)
        # if input_settings is not None:
        #     self.mappers = input_settings.pop("mappers", None)
        #     self.description = input_settings.pop("description", None)
        #     self.icons = input_settings.pop("icons", None)

        self.index = index

        # A bit scuffed, but
        for kwarg, value in kwargs.items():
            self._root[kwarg] = value

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def description(self) -> Optional[str]:
        return self._root[self._root_item]["settings"].get("description", None)

    @description.setter
    def description(self, value: Optional[str]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.UpgradePlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "description",
                value,
            )
            self._root[self._root_item]["settings"]["description"] = result
        else:
            self._root[self._root_item]["settings"]["description"] = value

    # =========================================================================

    @property
    def icons(self) -> Optional[list[Icon]]:
        return self._root[self._root_item]["settings"].get("icons", None)

    @icons.setter
    def icons(self, value: Union[list[str], list[Icon], None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.UpgradePlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "icons",
                value,
            )
            self._root[self._root_item]["settings"]["icons"] = result
        else:
            self._root[self._root_item]["settings"]["icons"] = value

    # =========================================================================

    @property
    def mapper_count(self) -> uint8:
        """
        The total number of unique mappings that this entity can have. Read only.

        :type: int
        """
        return items.raw[self.item]["mapper_count"]

    # =========================================================================

    @property
    def mappers(self) -> Optional[list[Mapper]]:
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
        return self._root[self._root_item]["settings"].get("mappers", None)

    @mappers.setter
    def mappers(self, value: Optional[list[Union[tuple[str, str], Mapper]]]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.UpgradePlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "mappers",
                value,
            )
            self._root[self._root_item]["settings"]["mappers"] = result
        else:
            self._root[self._root_item]["settings"]["mappers"] = value

    # =========================================================================

    @reissue_warnings
    def set_mapping(
        self, from_obj: Union[str, MapperID], to_obj: Union[str, MapperID], index: int
    ):
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

    def remove_mapping(
        self,
        from_obj: Union[str, MapperID],
        to_obj: Union[str, MapperID],
        index: Optional[int] = None,
    ):
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
            necessarily ``0``. If you want to remove the first entry in the
            mappers list, then you can simply do `del upgrade_planner.mappers[0]`.

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

    def pop_mapping(self, index: int) -> Mapper:
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

    # def validate(self) -> None:
    #     if self.is_valid:
    #         return

    #     # TODO: wrap with DataFormatError or similar
    #     UpgradePlanner.Format.model_validate(self._root)

    #     super().validate()

    # def inspect(self) -> ValidationResult:
    #     result = super().inspect()

    #     # By nature of necessity, we must ensure that all members of upgrade
    #     # planner are in a correct and known format, so we must call:
    #     try:
    #         self.validate()
    #     except Exception as e:
    #         # If validation fails, it's in a format that we do not expect; and
    #         # therefore unreasonable for us to assume that we can continue
    #         # checking for issues relating to that non-existent format.
    #         # Therefore, we add the errors to the error list and early exit
    #         # TODO: figure out the proper way to reraise
    #         result.error_list.append(DataFormatError(str(e)))
    #         return result

    #     # Keep track to see if multiple entries exist with the same index
    #     occupied_indices = {}
    #     # Check each mapper
    #     for mapper in self.mappers:
    #         # Ensure that "from" and "to" are a valid pair
    #         # We assert that index must exist in each mapper, but both "from"
    #         # and "to" may be omitted
    #         reasons = check_valid_upgrade_pair(
    #             mapper.get("from", None), mapper.get("to", None)
    #         )
    #         if reasons is not None:
    #             result.warning_list.extend(reasons)

    #         # If the index is greater than mapper_count, then the mapping will
    #         # be redundant
    #         if not mapper["index"] < self.mapper_count:
    #             result.warning_list.append(
    #                 IndexWarning(
    #                     "'index' ({}) for mapping '{}' to '{}' must be in range [0, {}) or else it will have no effect".format(
    #                         mapper["index"],
    #                         mapper["from"]["name"],
    #                         mapper["to"]["name"],
    #                         self.mapper_count,
    #                     )
    #                 )
    #             )

    #         # Keep track of entries that occupy the same index (only the last
    #         # mapping is used)
    #         if mapper["index"] in occupied_indices:
    #             occupied_indices[mapper["index"]]["count"] += 1
    #             occupied_indices[mapper["index"]]["mapper"] = mapper
    #         else:
    #             occupied_indices[mapper["index"]] = {"count": 0, "mapper": mapper}

    #     # Issue warnings if multiple mappers occupy the same index
    #     for spot in occupied_indices:
    #         entry = occupied_indices[spot]
    #         if entry["count"] > 0:
    #             result.warning_list.append(
    #                 IndexWarning(
    #                     "Mapping at index {} was overwritten {} time(s); final mapping is '{}' to '{}'".format(
    #                         spot,
    #                         entry["count"],
    #                         entry["mapper"].get("from", {"name": None})["name"],
    #                         entry["mapper"].get("to", {"name": None})["name"],
    #                     )
    #                 )
    #             )

    #     return result

    # def to_dict(self) -> dict:

    #     out_model = UpgradePlanner.Format.model_construct(**self._root)
    #     out_model.upgrade_planner = (
    #         UpgradePlanner.Format.UpgradePlannerObject.model_construct(
    #             **out_model.upgrade_planner
    #         )
    #     )
    #     # out_model.upgrade_planner.settings = UpgradePlanner.Format.UpgradePlannerObject.Settings.model_construct(**out_model.upgrade_planner.settings)
    #     # out_model.upgrade_planner.settings.icons = Icons.model_construct(out_model.upgrade_planner.settings.icons)
    #     # out_model.upgrade_planner.settings.mappers = Mappers.model_construct(out_model.upgrade_planner.settings.mappers)

    #     print("\tMODEL: ", out_model)

    #     out_dict = out_model.model_dump(
    #         by_alias=True,
    #         exclude_none=True,  # Trim if values are None
    #         exclude_defaults=True,  # This would be ideal, but problems arise
    #         warnings=False,  # Ignore warnings until model_construct is properly recursive
    #     )

    #     # TODO: Ideally this would also be part of the last step, but another
    #     # pydantic peculiarity
    #     if out_dict[self._root_item].get("settings", None) == {}:
    #         del out_dict[self._root_item]["settings"]

    #     return out_dict

    # def to_dict(self, exclude_none: bool = True, exclude_defaults: bool = True) -> dict:
    #     out_dict = self._root.model_dump(
    #         # Some attributes are reserved words ('type', 'from', etc.); this
    #         # resolves that issue
    #         by_alias=True,
    #         # Trim if values are None
    #         exclude_none=exclude_none,
    #         # Trim if values are defaults
    #         exclude_defaults=exclude_defaults,
    #         # Ignore warnings because we might export a model where the keys are
    #         # intentionally incorrect
    #         # Plus there are things like Associations with which we want to
    #         # preserve when returning this object so that a parent object can
    #         # handle them
    #         warnings=False,
    #     )

    #     return out_dict
