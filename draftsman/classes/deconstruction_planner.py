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
from draftsman.data import items
from draftsman.error import DataFormatError
from draftsman.warning import IndexWarning, UnknownEntityWarning, UnknownTileWarning
from draftsman.signatures import (
    Icon,
    DraftsmanBaseModel,
    EntityFilter,
    TileFilter,
    uint8,
    uint16,
    uint64,
    EntityName,
    TileName,
)
from draftsman.utils import encode_version, reissue_warnings

from pydantic import (
    ConfigDict,
    Field,
    ValidatorFunctionWrapHandler,
    ValidationInfo,
    ValidationError,
    field_validator,
)
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
                """,
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
                icons: Optional[list[Icon]] = Field(
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
                    """,
                )
                entity_filters: Optional[list[EntityFilter]] = Field(
                    [],
                    description="""
                    Either a list of entities to deconstruct, or a list of 
                    entities to not deconstruct, depending on the value of
                    'entity_filter_mode'.
                    """,
                )
                trees_and_rocks_only: Optional[bool] = Field(
                    False,
                    description="""
                    Whether or not to only deconstruct environmental objects
                    like trees and rocks. If true, all 'entity_filters' and
                    'tile_filters' are ignored, regardless of their modes.
                    """,
                )

                tile_filter_mode: Optional[FilterMode] = Field(
                    FilterMode.WHITELIST,
                    description="""
                    Whether to treat the 'tile_filters' list as a whitelist
                    or blacklist, where 0 is whitelist and 1 is blacklist.
                    """,
                )
                tile_filters: Optional[list[TileFilter]] = Field(
                    [],
                    description="""
                    Either a list of tiles to deconstruct, or a list of tiles to
                    not deconstruct, depending on the value of 
                    'tile_filter_mode'.""",
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

                @field_validator("entity_filters", mode="before")
                @classmethod
                def normalize_entity_filters(cls, value: Any):
                    if isinstance(value, (list, tuple)):
                        result = []
                        for i, entity in enumerate(value):
                            if isinstance(entity, str):
                                result.append({"index": i + 1, "name": entity})
                            else:
                                result.append(entity)
                        return result
                    else:
                        return value

                @field_validator("tile_filters", mode="before")
                @classmethod
                def normalize_tile_filters(cls, value: Any):
                    if isinstance(value, (list, tuple)):
                        result = []
                        for i, tile in enumerate(value):
                            if isinstance(tile, str):
                                result.append({"index": i + 1, "name": tile})
                            else:
                                result.append(tile)
                        return result
                    else:
                        return value

            settings: Optional[Settings] = Settings()

            @field_validator("version", mode="before")
            @classmethod
            def normalize_to_int(cls, value: Any):
                if isinstance(value, (list, tuple)):
                    return encode_version(*value)
                return value

        deconstruction_planner: DeconstructionPlannerObject
        index: Optional[uint16] = Field(
            None,
            description="""
            The index of the blueprint inside a parent BlueprintBook's blueprint
            list. Only meaningful when this object is inside a BlueprintBook.
            """,
        )

        model_config = ConfigDict(title="DeconstructionPlanner")

    # =========================================================================
    # Constructors
    # =========================================================================

    def __init__(
        self,
        deconstruction_planner: Union[str, dict, None] = None,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        if_unknown: str = "error",  # TODO: enum
    ):
        """
        TODO
        """
        self._root: __class__.Format

        print(deconstruction_planner)

        super().__init__(
            root_item="deconstruction_planner",
            root_format=DeconstructionPlanner.Format.DeconstructionPlannerObject,
            item="deconstruction-planner",
            init_data=deconstruction_planner,
            if_unknown=if_unknown,
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    @reissue_warnings
    def setup(
        self,
        label: str = None,
        version: uint64 = __factorio_version_info__,
        settings: Format.DeconstructionPlannerObject.Settings = {},
        index: Optional[uint16] = None,
        if_unknown: str = "error",  # TODO: enum
        **kwargs
    ):
        # Item (type identifier)
        kwargs.pop("item", None)

        self.label = label
        self.version = version

        if settings is not None:
            self.entity_filter_mode = settings.get(
                "entity_filter_mode", FilterMode.WHITELIST
            )
            self.entity_filters = settings.get("entity_filters", [])
            self.trees_and_rocks_only = settings.get("trees_and_rocks_only", False)

            self.tile_filter_mode = settings.get(
                "tile_filter_mode", FilterMode.WHITELIST
            )
            self.tile_filters = settings.get("tile_filters", [])
            self.tile_selection_mode = settings.get(
                "tile_selection_mode", TileSelectionMode.NEVER
            )

            self.description = settings.get("description", None)
            self.icons = settings.get("icons", None)

        self.index = index

        # A bit scuffed, but
        # Issue warnings for any keyword not recognized by UpgradePlanner
        for kwarg, value in kwargs.items():
            self._root[kwarg] = value

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def entity_filter_count(self) -> uint8:
        """
        TODO
        """
        return items.raw[self.item].get("entity_filter_count", 0)

    # =========================================================================

    @property
    def tile_filter_count(self) -> uint8:
        """
        TODO
        """
        return items.raw[self.item].get("tile_filter_count", 0)

    # =========================================================================

    @property
    def description(self) -> Optional[str]:
        return self._root[self._root_item]["settings"].get("description", None)

    @description.setter
    def description(self, value: Optional[str]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
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
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "icons",
                value,
            )
            self._root[self._root_item]["settings"]["icons"] = result
        else:
            self._root[self._root_item]["settings"]["icons"] = value

    # =========================================================================

    @property
    def entity_filter_mode(self) -> Optional[FilterMode]:
        """
        The method of filtering entities for deconstruction. Can be either ``0``
        (whitelist) or ``1`` (blacklist).

        :getter: Gets the entity filter mode, or ``None`` if not set.
        :setter: Sets the entity filter mode. Deletes the key if set to ``None``

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
                value,
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
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.DeconstructionPlannerObject.Settings,
                self._root[self._root_item]["settings"],
                "entity_filters",
                value,
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
                value,
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
                value,
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
                value,
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
                value,
            )
            self._root[self._root_item]["settings"]["tile_selection_mode"] = result
        else:
            self._root[self._root_item]["settings"]["tile_selection_mode"] = value

    # =========================================================================
    # Utility functions
    # =========================================================================

    def set_entity_filter(self, index: uint64, name: EntityName):
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
        if name is not None:
            try:
                new_entry = EntityFilter(index=index, name=name)
                new_entry.index += 1
            except ValidationError as e:
                raise DataFormatError(e) from None

        new_filters = self.entity_filters if self.entity_filters is not None else []

        found_index = None
        for i, filter in enumerate(new_filters):
            if filter["index"] == index + 1:
                if name is None:
                    del new_filters[i]
                else:
                    filter["name"] = name
                found_index = i
                break

        if found_index is None:
            # Otherwise its unique; add to list
            new_filters.append(new_entry)

        result = attempt_and_reissue(
            self,
            self.Format.DeconstructionPlannerObject.Settings,
            self._root[self._root_item]["settings"],
            "entity_filters",
            new_filters,
        )
        self._root[self._root_item]["settings"]["entity_filters"] = result

    def set_entity_filters(self, *entity_filters: list[str]):
        """
        Sets a tile filter in the list of tile filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.tile_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the tile to filter for deconstruction.
        """
        result = attempt_and_reissue(
            self,
            self.Format.DeconstructionPlannerObject.Settings,
            self._root[self._root_item]["settings"],
            "entity_filters",
            entity_filters,
        )
        self._root[self._root_item]["settings"]["entity_filters"] = result

    def set_tile_filter(self, index: uint64, name: TileName):
        """
        Sets a tile filter in the list of tile filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.tile_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the tile to filter for deconstruction.
        """
        # TODO: sorting with bisect
        if name is not None:
            try:
                new_entry = TileFilter(index=index, name=name)
                new_entry.index += 1
            except ValidationError as e:
                raise DataFormatError(e) from None

        new_filters = self.tile_filters if self.tile_filters is not None else []

        found_index = None
        for i, filter in enumerate(new_filters):
            if filter["index"] == index + 1:
                if name is None:
                    del new_filters[i]
                else:
                    filter["name"] = name
                found_index = i
                break

        if found_index is None:
            # Otherwise its unique; add to list
            new_filters.append(new_entry)

        result = attempt_and_reissue(
            self,
            self.Format.DeconstructionPlannerObject.Settings,
            self._root[self._root_item]["settings"],
            "tile_filters",
            new_filters,
        )
        self._root[self._root_item]["settings"]["tile_filters"] = result

    def set_tile_filters(self, *tile_names: list[str]):
        """
        TODO
        """
        for i, tile_name in enumerate(tile_names):
            self.set_tile_filter(i, tile_name)
