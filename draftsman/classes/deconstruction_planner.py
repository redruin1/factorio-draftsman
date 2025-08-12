# deconstruction_planner.py

from draftsman.classes.blueprintable import Blueprintable
from draftsman.constants import FilterMode, TileSelectionMode
from draftsman.data import items
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    Comparator,
    QualityID,
    uint8,
    EntityFilter,
    TileFilter,
)
from draftsman.validators import instance_of, try_convert

import attrs
import bisect
from typing import Literal


@attrs.define
class DeconstructionPlanner(Blueprintable):
    """
    Handles the deconstruction of entities. Has functionality to only select
    certain entities or tiles, as well as only natural objects like trees and
    rocks.
    """

    @property
    def root_item(self) -> Literal["deconstruction_planner"]:
        return "deconstruction_planner"

    # =========================================================================

    # TODO: should be an evolve
    item: str = attrs.field(
        default="deconstruction-planner",
        validator=instance_of(str),
        metadata={
            "omit": False,
        },
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Always the name of the corresponding Factorio item to this blueprintable
    instance. Read only.
    """

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
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The method of filtering entities for deconstruction.
    """

    # =========================================================================

    def _convert_entity_filters(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = EntityFilter(index=i, name=elem)
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
    .. serialized::

        This attribute is imported/exported from blueprint strings.
    
    The list of entity filters.
    """

    # =========================================================================

    trees_and_rocks_only: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to only deconstruct natural entities, such as trees and
    rocks.
    """

    # =========================================================================

    tile_filter_mode: FilterMode = attrs.field(
        default=FilterMode.WHITELIST,
        converter=try_convert(FilterMode),
        validator=instance_of(FilterMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The method of filtering tiles for deconstruction.
    """

    # =========================================================================

    def _convert_tile_filters(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = TileFilter(index=i, name=elem)
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
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The list of tile filters.
    """

    # =========================================================================

    tile_selection_mode: TileSelectionMode = attrs.field(
        default=TileSelectionMode.NORMAL,
        converter=try_convert(TileSelectionMode),
        validator=instance_of(TileSelectionMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The method of filtering entities for deconstruction.
    """

    # =========================================================================
    # Utility functions
    # =========================================================================

    def set_entity_filter(
        self,
        index: int,  # TODO: should be uint64
        name: str,  # TODO: should be EntityID
        quality: QualityID = "normal",
        comparator: Comparator = "=",
    ):
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
            new_entry = EntityFilter(
                index=index, name=name, quality=quality, comparator=comparator
            )
            bisect.insort(
                self.entity_filters, 
                new_entry, 
                key=lambda e: 0 if e.index is None else e.index
            )

    def set_tile_filter(
        self, index: int, name: str  # TODO: should be uint64  # TODO: should be TileID
    ):
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
            new_entry = TileFilter(index=index, name=name)
            bisect.insort(
                self.tile_filters, 
                new_entry, 
                key=lambda e: 0 if e.index is None else e.index
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
