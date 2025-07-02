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

from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import Exportable
from draftsman.constants import FilterMode, TileSelectionMode
from draftsman.data import items
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    uint8,
    uint64,
    EntityID,
    TileID,
)
from draftsman.validators import instance_of, try_convert

import attrs
from typing import Literal, Optional


@attrs.define
class DeconstructionPlanner(Blueprintable):
    """
    Handles the deconstruction of entities. Has functionality to only select
    certain entities or tiles, as well as only natural objects like trees and
    rocks.
    """

    @attrs.define
    class EntityFilter(Exportable):
        index: Optional[uint64] = attrs.field(validator=instance_of(uint64))
        """
        Position of the filter in the DeconstructionPlanner. Seems to 
        behave more like a sorting key rather than a numeric index; if omitted, 
        entities will be sorted by their Factorio order when imported instead
        of specific slots in the GUI, contrary to what index would seem to imply.
        """
        name: EntityID = attrs.field(validator=instance_of(EntityID))
        """
        The name of a valid deconstructable entity.
        """

    @attrs.define
    class TileFilter(Exportable):
        index: Optional[uint64] = attrs.field(validator=instance_of(uint64))
        """
        Position of the filter in the DeconstructionPlanner. Seems to 
        behave more like a sorting key rather than a numeric index; if omitted, 
        entities will be sorted by their Factorio order when imported instead
        of specific slots in the GUI, contrary to what index would seem to imply.
        """
        name: TileID = attrs.field(validator=instance_of(TileID))
        """
        The name of a valid deconstructable tile.
        """

    @property
    def root_item(self) -> Literal["deconstruction_planner"]:
        return "deconstruction_planner"

    # =========================================================================

    item: str = attrs.field(
        default="deconstruction-planner",
        validator=instance_of(str),
        metadata={
            "omit": False,
        },
    )
    # TODO: description

    # =========================================================================

    @property
    def entity_filter_count(self) -> uint8:
        """
        The total number of entity filters that this DeconstructionPlanner can
        support simultaneously.
        """
        return items.raw[self.item].get("entity_filter_count", 0)

    # =========================================================================

    @property
    def tile_filter_count(self) -> uint8:
        """
        The total number of tile filters that this DeconstructionPlanner can
        support simultaneously.
        """
        return items.raw[self.item].get("tile_filter_count", 0)

    # =========================================================================

    entity_filter_mode: FilterMode = attrs.field(
        default=FilterMode.WHITELIST,
        converter=try_convert(FilterMode),
        validator=instance_of(FilterMode),
    )
    """
    The method of filtering entities for deconstruction. Can be either ``0``
    (whitelist) or ``1`` (blacklist).

    :raises ValueError: If not set to an valid :py:data:`.FilterMode` or
        ``None``.
    """

    # =========================================================================

    def _convert_entity_filters(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = DeconstructionPlanner.EntityFilter(index=i, name=elem)
                else:
                    res[i] = elem
            return res
        else:
            return value

    entity_filters: list[EntityFilter] = attrs.field(
        factory=list,
        converter=_convert_entity_filters,
        validator=instance_of(list[EntityFilter]),
    )
    """
    The list of entity filters.
    """

    # =========================================================================

    trees_and_rocks_only: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    Whether or not to only deconstruct natural entities, such as trees and
    rocks.

    :raises TypeError: If set to anything other than a ``bool`` or ``None``.
    """

    # =========================================================================

    tile_filter_mode: FilterMode = attrs.field(
        default=FilterMode.WHITELIST,
        converter=try_convert(FilterMode),
        validator=instance_of(FilterMode),
    )
    """
    The method of filtering tiles for deconstruction. Can be either ``0``
    (whitelist) or ``1`` (blacklist).

    :raises DataFormatError: If not set to an valid :py:data:`.FilterMode`.
    """

    # =========================================================================

    def _convert_tile_filters(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = DeconstructionPlanner.TileFilter(index=i, name=elem)
                else:
                    res[i] = elem
            return res
        else:
            return value

    tile_filters: list[TileFilter] = attrs.field(
        factory=list,
        converter=_convert_tile_filters,
        validator=instance_of(list[TileFilter]),
    )
    """
    The list of tile filters.
    """

    # =========================================================================

    tile_selection_mode: TileSelectionMode = attrs.field(
        default=TileSelectionMode.NORMAL,
        converter=try_convert(TileSelectionMode),
        validator=instance_of(TileSelectionMode),
    )
    """
    The method of filtering entities for deconstruction. Valid modes are:

    0. ``NORMAL`` (default): Only selects tiles if no entities are selected.
    1. ``ALWAYS``: Always includes tiles in selection.
    2. ``NEVER``: Never includes tiles in selection.
    3. ``ONLY``: Ignores entities, and only selects tiles.

    :raises ValueError: If not set to a valid :py:data:`.TileSelectionMode`
        or ``None``.
    """

    # =========================================================================
    # Utility functions
    # =========================================================================

    def set_entity_filter(self, index: uint64, name: EntityID):
        """
        Sets an entity filter in the list of entity filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.entity_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the entity to filter for deconstruction.
        """
        found_index = None
        for i, filter in enumerate(self.entity_filters):
            if filter.index == index:
                if name is None:
                    del self.entity_filters[i]
                else:
                    filter.name = name
                found_index = i
                break

        if found_index is None:
            # Otherwise its unique; add to list
            new_entry = DeconstructionPlanner.EntityFilter(index=index, name=name)
            # TODO: sorting with bisect
            self.entity_filters.append(new_entry)

    def set_entity_filters(self, *entity_names: list[str]):
        """
        Sets a tile filter in the list of tile filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.tile_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the tile to filter for deconstruction.
        """
        for i, entity_name in enumerate(entity_names):
            self.set_entity_filter(i, entity_name)

    def set_tile_filter(self, index: uint64, name: TileID):
        """
        Sets a tile filter in the list of tile filters. Appends the new one
        to the end of the list regardless of the ``index``. If ``index`` is
        already occupied with a different filter it is overwritten with the new
        one; does nothing if the exact filter already exists within
        :py:attr:`.tile_filters`.

        :param index: The index to set the new filter at.
        :param name: The name of the tile to filter for deconstruction.
        """

        found_index = None
        for i, filter in enumerate(self.tile_filters):
            if filter.index == index:
                if name is None:
                    del self.tile_filters[i]
                else:
                    filter.name = name
                found_index = i
                break

        if found_index is None:
            # Otherwise its unique; add to list
            new_entry = DeconstructionPlanner.TileFilter(index=index, name=name)
            # TODO: sorting with bisect
            self.tile_filters.append(new_entry)

    def set_tile_filters(self, *tile_names: list[str]):
        """
        TODO
        """
        for i, tile_name in enumerate(tile_names):
            self.set_tile_filter(i, tile_name)


draftsman_converters.add_hook_fns(
    DeconstructionPlanner.EntityFilter,
    lambda fields: {
        "name": fields.name.name,
        "index": fields.index.name,
    },
)


draftsman_converters.add_hook_fns(
    DeconstructionPlanner.TileFilter,
    lambda fields: {
        "name": fields.name.name,
        "index": fields.index.name,
    },
)


draftsman_converters.add_hook_fns(
    DeconstructionPlanner,
    lambda fields: {
        ("deconstruction_planner", "item"): fields.item.name,
        ("deconstruction_planner", "label"): fields.label.name,
        ("deconstruction_planner", "label_color"): fields.label_color.name,
        ("deconstruction_planner", "settings", "description"): fields.description.name,
        ("deconstruction_planner", "settings", "icons"): fields.icons.name,
        (
            "deconstruction_planner",
            "settings",
            "entity_filter_mode",
        ): fields.entity_filter_mode.name,
        (
            "deconstruction_planner",
            "settings",
            "entity_filters",
        ): fields.entity_filters.name,
        (
            "deconstruction_planner",
            "settings",
            "trees_and_rocks_only",
        ): fields.trees_and_rocks_only.name,
        (
            "deconstruction_planner",
            "settings",
            "tile_filter_mode",
        ): fields.tile_filter_mode.name,
        (
            "deconstruction_planner",
            "settings",
            "tile_filters",
        ): fields.tile_filters.name,
        (
            "deconstruction_planner",
            "settings",
            "tile_selection_mode",
        ): fields.tile_selection_mode.name,
        ("deconstruction_planner", "settings"): None,
        ("deconstruction_planner", "version"): fields.version.name,
    },
)
