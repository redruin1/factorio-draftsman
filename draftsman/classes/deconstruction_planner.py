# deconstruction_planner.py

"""
.. code-block:: python

    {
        "deconstruction_planner": {
            "item": "deconstruction-planner", # The associated item with this structure
            "label": str, # A user given name for this deconstruction planner
            "version": int, # The encoded version of Factorio this planner was created 
                            # with/designed for (64 bits)
            "settings": {
                "entity_filter_mode": int, # 0 = Whitelist, 1 = Blacklist
                "entity_filters": [ # A list of entities to deconstruct
                    {
                        "name": str, # Name of the entity
                        "index": int # Index of the entity in the list in range [1, 30]
                    },
                    ... # Up to 30 filters total
                ]
                "trees_and_rocks_only": bool, # Self explanatory, disables everything 
                                              # else
                "tile_filter_mode": int, # 0 = Whitelist, 1 = Blacklist
                "tile_filters": [ # A list of tiles to deconstruct
                    {
                        "name": str, # Name of the tile
                        "index": int # Index of the tile in the list in range [1, 30]
                    },
                    ... # Up to 30 filters total
                ]
                "tile_selection_mode": int, # 0 = Normal, 1 = Always, 2 = Never, 
                                            # 3 = Only
                "description": str, # A user given description for this deconstruction 
                                    # planner
                "icons": [ # A set of signals to act as visual identification
                    {
                        "signal": {"name": str, "type": str}, # Name and type of signal
                        "index": int, # In range [1, 4], starting top-left and moving across
                    },
                    ... # Up to 4 icons total
                ],
            }
        }
    }
"""

from draftsman import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import ValidationResult, attempt_and_reissue
from draftsman.constants import FilterMode, TileSelectionMode, ValidationMode
from draftsman.data import entities, tiles
from draftsman.error import DataFormatError
from draftsman.warning import IndexWarning, UnknownEntityWarning, UnknownTileWarning
from draftsman.signatures import (
    Icons,
    DraftsmanBaseModel,
    EntityFilter,
    TileFilter,
    uint8,
    uint16,
    uint64,
)
from draftsman.utils import encode_version, reissue_warnings

from pydantic import ConfigDict, Field, field_validator
from typing import Any, Literal, Optional, Sequence, Union


class DeconstructionPlanner(Blueprintable):
    """
    Handles the deconstruction of entities. Has functionality to only select
    certain entities or tiles, as well as only natural objects like trees and
    rocks.
    """

    # =========================================================================
    # Format
    # =========================================================================

    class Format(DraftsmanBaseModel):
        class DeconstructionPlannerObject(DraftsmanBaseModel):
            item: Literal["deconstruction-planner"] = Field(
                ...,
                description="""
                The item that this DeconstructionItem object is associated with. 
                Always equivalent to 'deconstruction-planner'.
                """
            )
            label: Optional[str] = Field(
                None,
                description="""
                A string title for this DeconstructionPlanner.
                """,
            )
            version: Optional[uint64] = Field(
                None,
                description="""
                What version of Factorio this DeconstructionPlanner was made 
                in/intended for. Specified as 4 unsigned 16-bit numbers combined, 
                representing the major version, the minor version, the patch 
                number, and the internal development version respectively. The 
                most significant digits correspond to the major version, and the 
                least to the development number. 
                """,
            )

            class Settings(DraftsmanBaseModel):
                """
                Contains information about the Deconstruction Planner's behavior,
                as well as additional metadata like it's description.
                """

                description: Optional[str] = Field(
                    None,
                    description="""
                    A string description given to this DeconstructionPlanner.
                    """,
                )
                icons: Optional[Icons] = Field(
                    None,
                    description="""
                    A set of signal pictures to associate with this 
                    DeconstructionPlanner.
                    """,
                )

                entity_filter_mode: Optional[FilterMode] = Field(
                    FilterMode.WHITELIST,
                    description="""
                    Whether to treat the 'entity_filters' list as a whitelist
                    or blacklist, where 0 is whitelist and 1 is blacklist.
                    """
                )
                entity_filters: Optional[list[EntityFilter]] = Field(
                    [],
                    description="""
                    Either a list of entities to deconstruct, or a list of 
                    entities to not deconstruct, depending on the value of
                    'entity_filter_mode'.
                    """
                )
                trees_and_rocks_only: Optional[bool] = Field(
                    False,
                    description="""
                    Whether or not to only deconstruct environmental objects
                    like trees and rocks. If true, all 'entity_filters' and
                    'tile_filters' are ignored, regardless of their modes.
                    """
                )

                tile_filter_mode: Optional[FilterMode] = Field(
                    FilterMode.WHITELIST,
                    description="""
                    Whether to treat the 'tile_filters' list as a whitelist
                    or blacklist, where 0 is whitelist and 1 is blacklist.
                    """
                )
                tile_filters: Optional[list[TileFilter]] = Field(
                    [],
                    description="""
                    Either a list of tiles to deconstruct, or a list of tiles to
                    not deconstruct, depending on the value of 
                    'tile_filter_mode'."""
                )
                tile_selection_mode: Optional[TileSelectionMode] = Field(
                    TileSelectionMode.NEVER,
                    description="""
                    The manner in which to select tiles for deconstruction. 
                    There are 4 modes:
                    
                    0 (Normal): Only select tiles for deconstruction when there
                        are no entities in the area,
                    1 (Always): Any valid tiles are always selected within the
                        area,
                    2 (Never): Tiles are never selected; if there are tiles 
                        defined in 'tile_filters', they are ignored,
                    3 (Only): Only tiles are selected; if there are entities
                        defined in 'entity_filters', they are ignored.
                    """
                )

            settings: Optional[Settings] = Settings()

            @field_validator("version", mode="before")
            @classmethod
            def normalize_to_int(cls, value: Any):
                if isinstance(value, Sequence):
                    return encode_version(*value)
                return value

        deconstruction_planner: DeconstructionPlannerObject
        index: Optional[uint16] = Field(
            None, 
            description="""
            The index of the blueprint inside a parent BlueprintBook's blueprint
            list. Only meaningful when this object is inside a BlueprintBook.
            """
        )

        model_config = ConfigDict(title="DeconstructionPlanner")

    # =========================================================================
    # Constructors
    # =========================================================================

    def __init__(
        self, 
        deconstruction_planner: Union[str, dict] = None, 
        index: uint16 = None,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
        """
        TODO
        """
        self._root: __class__.Format

        super().__init__(
            root_item="deconstruction_planner",
            root_format=DeconstructionPlanner.Format.DeconstructionPlannerObject,
            item="deconstruction-planner",
            init_data=deconstruction_planner,
            index=index,
        )

        self.validate_assignment = validate_assignment

        if validate:
            self.validate(mode=validate).reissue_all(stacklevel=3)

    @reissue_warnings
    def setup(
        self, 
        label: str = None,
        version: uint64 = __factorio_version_info__,
        settings: Format.DeconstructionPlannerObject.Settings = Format.DeconstructionPlannerObject.Settings(),
        index: uint16 = None,
        **kwargs
    ):
        # self._root[self._root_item]["settings"] = __class__.Format.DeconstructionPlannerObject.Settings()

        # Item (type identifier)
        # self._root[self._root_item]["item"] = "deconstruction-planner"
        kwargs.pop("item", None)

        self.label = label
        self.version = version
        self._root[self._root_item]["settings"] = settings

        # settings = kwargs.pop("settings", None)
        # if settings is not None:
        #     self.entity_filter_mode = settings.pop("entity_filter_mode", None)
        #     self.entity_filters = settings.pop("entity_filter_mode", None)
        #     self.trees_and_rocks_only = settings.pop("trees_and_rocks_only", None)

        #     self.tile_filter_mode = settings.pop("tile_filter_mode", None)
        #     self.tile_filters = settings.pop("tile_filters", None)
        #     self.tile_selection_mode = settings.pop("tile_selection_mode", None)

        #     self.description = settings.pop("description", None)
        #     self.icons = settings.pop("icons", None)

        self.index = index

        # A bit scuffed, but
        for kwarg, value in kwargs.items():
            self._root[kwarg] = value

        # Issue warnings for any keyword not recognized by UpgradePlanner
        # for unused_arg in kwargs:
        #     warnings.warn(
        #         "{} has no attribute '{}'".format(type(self), unused_arg),
        #         DraftsmanWarning,
        #         stacklevel=2,
        #     )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def entity_filter_count(self) -> uint8:
        """
        TODO
        """
        return entities.raw[self.item].get("entity_filter_count", 0)

    # =========================================================================

    @property
    def tile_filter_count(self) -> uint8:
        """
        TODO
        """
        return entities.raw[self.item].get("tile_filter_count", 0)

    # =========================================================================

    @property
    def entity_filter_mode(self) -> Optional[FilterMode]:
        """
        The method of filtering entities for deconstruction. Can be either ``0``
        (whitelist) or ``1`` (blacklist).

        :getter: Gets the entity filter mode, or ``None`` if not set.
        :setter: Sets the entity filter mode. Deletes the key if set to ``None``.
        :type: :py:data:`.FilterMode`

        :raises ValueError: If not set to an valid :py:data:`.FilterMode` or
            ``None``.
        """
        return self._root[self._root_item]["settings"].get("entity_filter_mode", None)

    @entity_filter_mode.setter
    def entity_filter_mode(self, value: Optional[FilterMode]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "entity_filter_mode",
                value
            )
            self._root[self._root_item]["settings"]["entity_filter_mode"] = result
        else:
            self._root[self._root_item]["settings"]["entity_filter_mode"] = value

    # =========================================================================

    @property
    def entity_filters(self) -> Optional[list[EntityFilter]]:
        """
        The list of entity filters.
        TODO
        TODO: shorthand with list
        """
        return self._root[self._root_item]["settings"].get("entity_filters", None)

    @entity_filters.setter
    def entity_filters(self, value: Optional[list[EntityFilter]]):
        # TODO: what if index >= self.entity_filter_count?
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "entity_filters",
                value
            )
            self._root[self._root_item]["settings"]["entity_filters"] = result
        else:
            self._root[self._root_item]["settings"]["entity_filters"] = value

    # =========================================================================

    @property
    def trees_and_rocks_only(self) -> Optional[bool]:
        """
        Whether or not to only deconstruct natural entities, such as trees and
        rocks.

        :getter: Gets the flag, or returns ``None`` if not set.
        :setter: Sets the flag, or deletes the key if set to ``None``.
        :type: ``bool``

        :raises TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._root[self._root_item]["settings"].get("trees_and_rocks_only", None)

    @trees_and_rocks_only.setter
    def trees_and_rocks_only(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "trees_and_rocks_only",
                value
            )
            self._root[self._root_item]["settings"]["trees_and_rocks_only"] = result
        else:
            self._root[self._root_item]["settings"]["trees_and_rocks_only"] = value

    # =========================================================================

    @property
    def tile_filter_mode(self) -> Optional[FilterMode]:
        """
        The method of filtering tiles for deconstruction. Can be either ``0``
        (whitelist) or ``1`` (blacklist).

        :getter: Gets the tile filter mode, or ``None`` if not set.
        :setter: Sets the tile filter mode. Deletes the key if set to ``None``.
        :type: :py:data:`.FilterMode`

        :raises ValueError: If not set to an valid :py:data:`.FilterMode` or
            ``None``.
        """
        return self._root[self._root_item]["settings"].get("tile_filter_mode", None)

    @tile_filter_mode.setter
    def tile_filter_mode(self, value: Optional[FilterMode]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "tile_filter_mode",
                value
            )
            self._root[self._root_item]["settings"]["tile_filter_mode"] = result
        else:
            self._root[self._root_item]["settings"]["tile_filter_mode"] = value

    # =========================================================================

    @property
    def tile_filters(self) -> Optional[list[TileFilter]]:
        """
        The list of tile filters.
        TODO
        """
        return self._root[self._root_item]["settings"].get("tile_filters", None)

    @tile_filters.setter
    def tile_filters(self, value: Optional[list[TileFilter]]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "tile_filters",
                value
            )
            self._root[self._root_item]["settings"]["tile_filters"] = result
        else:
            self._root[self._root_item]["settings"]["tile_filters"] = value

    # TODO: set_tile_filters() function

    # =========================================================================

    @property
    def tile_selection_mode(self) -> Optional[TileSelectionMode]:
        """
        The method of filtering entities for deconstruction. Valid modes are:

        0. ``NORMAL`` (default)
        1. ``ALWAYS``
        2. ``NEVER``
        3. ``ONLY``

        :getter: Gets the entity filter mode, or ``None`` if not set.
        :setter: Sets the entity filter mode. Deletes the key if set to ``None``.
        :type: :py:data:`.TileSelectionMode`

        :raises ValueError: If not set to a valid :py:data:`.TileSelectionMode`
            or ``None``.
        """
        return self._root[self._root_item]["settings"].get("tile_selection_mode", None)

    @tile_selection_mode.setter
    def tile_selection_mode(self, value: Optional[TileSelectionMode]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "tile_selection_mode",
                value
            )
            self._root[self._root_item]["settings"]["tile_selection_mode"] = result
        else:
            self._root[self._root_item]["settings"]["tile_selection_mode"] = value

    # =========================================================================
    # Utility functions
    # =========================================================================

    def set_entity_filter(self, index, name):
        # type: (int, str) -> None
        """
        Sets an entity filter in the list of entity filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.entity_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the entity to filter for deconstruction.
        """
        # TODO: sorting with bisect
        if self.entity_filters is None:
            self.entity_filters = []

        # Check if index is ouside the range of the max filter slots
        # if not 0 <= index < 30:
        #     raise IndexError(
        #         "Index {} exceeds the maximum number of entity filter slots (30)".format(
        #             index
        #         )
        #     )

        # Check to see that `name` is a valid entity
        # TODO

        for i in range(len(self.entity_filters)):
            filter = self.entity_filters[i]
            if filter["index"] == index + 1:
                if name is None:
                    del self.entity_filters[i]
                else:
                    filter["name"] = name
                return

        # Otherwise its unique; add to list
        self.entity_filters.append({"index": index + 1, "name": name})

    def set_entity_filters(self, *entity_names: list[str]):
        """
        TODO
        """
        for i, entity_name in enumerate(entity_names):
            self.set_entity_filter(i, entity_name)

    def set_tile_filter(self, index, name):
        # type: (int, str) -> None
        """
        Sets a tile filter in the list of tile filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.tile_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the tile to filter for deconstruction.
        """
        if self.tile_filters is None:
            self.tile_filters = []

        # Check if `index` is ouside the range of the max filter slots
        # if not 0 <= index < 30:
        #     raise IndexError(
        #         "Index {} exceeds the maximum number of tile filter slots (30)".format(
        #             index
        #         )
        #     )

        # Check to see that `name` is a valid tile
        # TODO

        for i in range(len(self.tile_filters)):
            filter = self.tile_filters[i]
            if filter["index"] == index + 1:
                if name is None:
                    del self.tile_filters[i]
                else:
                    filter["name"] = name
                return

        # Otherwise its unique; add to list
        self.tile_filters.append({"index": index + 1, "name": name})

    def set_tile_filters(self, *tile_names: list[str]):
        """
        TODO
        """
        for i, tile_name in enumerate(tile_names):
            self.set_tile_filter(i, tile_name)

    # =========================================================================

    # def validate(self):
    #     """
    #     TODO
    #     """
    #     if self.is_valid:
    #         return

    #     # TODO: wrap with DataFormatError or similar
    #     # TODO: this is a bit confusingly named, but it shouldn't matter for
    #     # the end user
    #     DeconstructionPlanner.Format.DeconstructionPlannerObject.model_validate(
    #         self._root
    #     )

    #     super().validate()

    def inspect(self) -> ValidationResult:
        result = super().inspect()

        # By nature of necessity, we must ensure that all members of upgrade
        # planner are in a correct and known format, so we must call:
        try:
            self.validate()
        except Exception as e:
            # If validation fails, it's in a format that we do not expect; and
            # therefore unreasonable for us to assume that we can continue
            # checking for issues relating to that non-existent format.
            # Therefore, we add the errors to the error list and early exit
            # TODO: figure out the proper way to reraise
            result.error_list.append(DataFormatError(str(e)))
            return result

        for entity_filter in self.entity_filters:
            if not 0 <= entity_filter["index"] < 30:
                result.warning_list.append(
                    IndexWarning(
                        "Index of entity_filter '{}' ({}) exceeds the maximum number of tile filter slots (30)".format(
                            entity_filter["name"], entity_filter["index"]
                        )
                    )
                )

            if entity_filter["name"] not in entities.raw:
                result.warning_list.append(
                    UnknownEntityWarning(
                        "Unrecognized entity '{}'".format(entity_filter["name"])
                    )
                )

        for tile_filter in self.tile_filters:
            if not 0 <= tile_filter["index"] < 30:
                result.warning_list.append(
                    IndexWarning(
                        "Index of entity_filter '{}' ({}) exceeds the maximum number of tile filter slots (30)".format(
                            tile_filter["name"], tile_filter["index"]
                        )
                    )
                )

            if tile_filter["name"] not in tiles.raw:
                result.warning_list.append(
                    UnknownTileWarning(
                        "Unrecognized tile '{}'".format(entity_filter["name"])
                    )
                )

        return result

    # def to_dict(self):
    #     out_model = DeconstructionPlanner.Format.model_construct(**self._root)
    #     out_model.deconstruction_planner = (
    #         DeconstructionPlanner.Format.DeconstructionPlannerObject.model_construct(
    #             **out_model.deconstruction_planner
    #         )
    #     )
    #     out_model.deconstruction_planner.settings = DeconstructionPlanner.Format.DeconstructionPlannerObject.Settings.model_construct(
    #         **out_model.deconstruction_planner.settings
    #     )

    #     print(out_model)

    #     # We then create an output dict
    #     out_dict = out_model.model_dump(
    #         by_alias=True,
    #         exclude_none=True,
    #         exclude_defaults=True,
    #         warnings=False,  # Ignore warnings until model_construct is recursive
    #     )

    #     return out_dict
