# deconstruction_planner.py
# -*- encoding: utf-8 -*-

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

from __future__ import unicode_literals

from draftsman import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.constants import FilterMode, TileSelectionMode
from draftsman.data import items
from draftsman.error import DataFormatError, InvalidItemError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import DraftsmanWarning

import copy
from schema import SchemaError
import six
from typing import Union
import warnings


class DeconstructionPlanner(Blueprintable):
    """
    Handles the deconstruction of entities. Has functionality to only select
    certain entities or tiles, as well as only natrual objects like trees and
    rocks.
    """

    @utils.reissue_warnings
    def __init__(self, deconstruction_planner=None):
        # type: (Union[str, dict]) -> None
        """
        TODO
        """
        super(DeconstructionPlanner, self).__init__(
            root_item="deconstruction_planner",
            item="deconstruction-planner",
            init_data=deconstruction_planner,
        )

    @utils.reissue_warnings
    def setup(self, **kwargs):
        self._root = {}
        self._root["settings"] = {}

        # Item (type identifier)
        self._root["item"] = "deconstruction-planner"
        kwargs.pop("item", None)

        self.label = kwargs.pop("label", None)

        if "version" in kwargs:
            self.version = kwargs.pop("version")
        else:
            self.version = utils.encode_version(*__factorio_version_info__)

        settings = kwargs.pop("settings", None)
        if settings is not None:
            self.entity_filter_mode = settings.pop("entity_filter_mode", None)
            self.entity_filters = settings.pop("entity_filter_mode", None)
            self.trees_and_rocks_only = settings.pop("trees_and_rocks_only", None)

            self.tile_filter_mode = settings.pop("tile_filter_mode", None)
            self.tile_filters = settings.pop("tile_filters", None)
            self.tile_selection_mode = settings.pop("tile_selection_mode", None)

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
    def entity_filter_mode(self):
        # type: () -> FilterMode
        """
        TODO
        """
        return self._root["settings"].get("entity_filter_mode", None)

    @entity_filter_mode.setter
    def entity_filter_mode(self, value):
        # type: (FilterMode) -> None
        if value is None:
            self._root["settings"].pop("entity_filter_mode", None)
        else:
            self._root["settings"]["entity_filter_mode"] = FilterMode(value)

    # =========================================================================

    @property
    def entity_filters(self):
        # type: () -> list[dict]
        """
        TODO
        """
        return self._root["settings"].get("entity_filters", None)

    @entity_filters.setter
    def entity_filters(self, value):
        # type: (list[dict]) -> None
        # TODO: what if index >= 30?
        if value is None:
            self._root["settings"].pop("entity_filters", None)
        else:
            try:
                value = signatures.FILTERS.validate(value)
                self._root["settings"]["entity_filters"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError, e)

    # =========================================================================

    @property
    def trees_and_rocks_only(self):
        # type: () -> bool
        """
        TODO
        """
        return self._root["settings"].get("trees_and_rocks_only", None)

    @trees_and_rocks_only.setter
    def trees_and_rocks_only(self, value):
        # type: (bool) -> None
        if value is None:
            self._root["settings"].pop("trees_and_rocks_only", None)
        elif isinstance(value, bool):
            self._root["settings"]["trees_and_rocks_only"] = value
        else:
            raise TypeError("'trees_and_rocks_only' must be either a bool or None")

    # =========================================================================

    @property
    def tile_filter_mode(self):
        # type: () -> FilterMode
        """
        TODO
        """
        return self._root["settings"].get("tile_filter_mode", None)

    @tile_filter_mode.setter
    def tile_filter_mode(self, value):
        # type: (FilterMode) -> None
        if value is None:
            self._root["settings"].pop("tile_filter_mode", None)
        else:
            self._root["settings"]["tile_filter_mode"] = FilterMode(value)

    # =========================================================================

    @property
    def tile_filters(self):
        # type: () -> list[dict]
        """
        TODO
        """
        return self._root["settings"].get("tile_filters", None)

    @tile_filters.setter
    def tile_filters(self, value):
        # type: (list[dict]) -> None
        if value is None:
            self._root["settings"].pop("tile_filters", None)
        else:
            try:
                value = signatures.FILTERS.validate(value)
                self._root["settings"]["tile_filters"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError, e)

    # =========================================================================

    @property
    def tile_selection_mode(self):
        # type: () -> TileSelectionMode
        """
        TODO
        """
        return self._root["settings"].get("tile_selection_mode", None)

    @tile_selection_mode.setter
    def tile_selection_mode(self, value):
        # type: (TileSelectionMode) -> None
        if value is None:
            self._root["settings"].pop("tile_selection_mode", None)
        else:
            self._root["settings"]["tile_selection_mode"] = TileSelectionMode(value)

    # =========================================================================
    # Utility functions
    # =========================================================================

    def set_entity_filter(self, index, name):
        # type: (int, str) -> None
        """
        TODO
        """
        if self.entity_filters is None:
            self.entity_filters = []

        # Check if index is ouside the range of the max filter slots
        if not 0 <= index < 30:
            raise IndexError(
                "Index {} exceeds the maximum number of entity filter slots (30)".format(
                    index
                )
            )

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

    def set_tile_filter(self, index, name):
        # type: (int, str) -> None
        """
        TODO
        """
        if self.tile_filters is None:
            self.tile_filters = []

        # Check if `index` is ouside the range of the max filter slots
        if not 0 <= index < 30:
            raise IndexError(
                "Index {} exceeds the maximum number of tile filter slots (30)".format(
                    index
                )
            )

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

    def to_dict(self):
        out_dict = copy.deepcopy(self._root)

        if out_dict["settings"] == {}:
            out_dict["settings"] = None  # null

        return {"deconstruction_planner": out_dict}
