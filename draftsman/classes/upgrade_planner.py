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
                        "from": {
                            "name": str, # The name of a valid replacable entity/item
                            "type": "entity" or "item" # Depending on name
                        },
                        "to": {
                            "name": str, # The name of a different, corresponding entity/item
                            "type": "entity" or "item" # Depending on name
                        },
                        "index": int # in range [1, 24]
                    },
                    .. # Up to 24 mappers total
                ],
                "description": str, # A user given description for this upgrade planner
                "icons": [ # A set of signals to act as visual identification
                    {
                        "signal": {"name": str, "type": str}, # Name and type of signal
                        "index": int, # In range [1, 4], starting top-left and moving across
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
from draftsman.data import items
from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import ItemLimitationWarning, ValueWarning, DraftsmanWarning

import copy

# import deal # TODO
from schema import SchemaError
import six
from typing import Union, Sequence
import warnings


# def get_allowed_items():
#     """
#     TODO
#     """
#     result = set()

#     return result

# _allowed_items = get_allowed_items()

# def equivalent_upgrade_types(a, b):
#     """
#     TODO
#     """
#     return True


class UpgradePlanner(Blueprintable):
    """
    A :py:class:`.Blueprintable` used to upgrade and downgrade entities and
    items.
    """

    @utils.reissue_warnings
    def __init__(self, upgrade_planner=None):
        # type: (Union[str, dict]) -> None
        """
        Constructs a new :py:class:`.UpgradePlanner`.

        :param upgrade_planner: Either a dictionary containing all the key
            attributes to set, or
        """
        super(UpgradePlanner, self).__init__(
            root_item="upgrade_planner",
            item="upgrade-planner",
            init_data=upgrade_planner,
        )

    @utils.reissue_warnings
    def setup(self, **kwargs):
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

    # TODO
    # @property
    # def allowed_items(self):
    #     return _allowed_items

    @property
    def mappers(self):
        # type: () -> list
        """
        The list of mappings of one entity or item type to the other entity or
        item type.

        :raises DataFormatError: If setting this attribute and any of the
            entries in the list do not match the format specified above.

        :getter:
        :setter:
        :type: TODO
        """
        return self._root["settings"].get("mappers", None)

    @mappers.setter
    def mappers(self, value):
        # type: (Union[list[dict], list[tuple]]) -> None
        if value is None:
            del self._root["settings"]["mappers"]
            return

        self._root["settings"]["mappers"] = []
        for i, mapper in enumerate(value):
            if isinstance(mapper, dict):
                self.set_mapping(
                    mapper.get("from", None), mapper.get("to", None), mapper["index"]
                )
            elif isinstance(mapper, Sequence):
                self.set_mapping(mapper[0], mapper[1], i)
            else:
                raise DataFormatError(
                    "{} cannot be resolved to a UpgradePlanner Mapping"
                )

    # @deal.pre(
    #     lambda _: signatures.SIGNAL_ID_OR_NONE.is_valid(_.from_obj),
    #     message="'from_obj' cannot be resolved to a valid SIGNAL_ID"
    # )
    # @deal.pre(
    #     lambda _: signatures.SIGNAL_ID_OR_NONE.is_valid(_.to_obj),
    #     message="'from_obj' cannot be resolved to a valid SIGNAL_ID"
    # )
    # @deal.pre(
    #     lambda _: isinstance(_.index, int),
    #     message="'index' is not an integer"
    # )
    # @deal.pre(
    #     lambda _: 0 <= _.index < 24,
    #     message="'index' must be in range [0, 24)"
    # )
    @utils.reissue_warnings
    def set_mapping(self, from_obj, to_obj, index):
        # type: (Union[str, dict], Union[str, dict], int) -> None
        """
        Sets a single mapping in the :py:class:`.UpgradePlanner`.

        :param from_obj: The :py:data:`.SIGNAL_ID` to to convert entities/items
            from.
        :param to_obj: The :py:data:`.SIGNAL_ID` to convert entities/items to.
        """
        # Check types of all parameters (SIGNAL_ID, SIGNAL_ID, int)
        try:
            from_obj = signatures.SIGNAL_ID_OR_NONE.validate(from_obj)
            to_obj = signatures.SIGNAL_ID_OR_NONE.validate(to_obj)
            index = signatures.INTEGER.validate(index)
        except SchemaError as e:
            six.raise_from(DataFormatError, e)

        # TODO
        # Check both from_obj and to_obj to make sure that both are valid inputs
        # in the context of an upgrade planner
        # if from_obj["name"] not in _allowed_items:
        #     warnings.warn(
        #         "'{}' is not an allowed upgradable item".format(from_obj["name"]),
        #         ItemLimitationWarning,
        #         stacklevel=2,
        #     )
        # if to_obj["name"] not in _allowed_items:
        #     warnings.warn(
        #         "'{}' is not an allowed upgradable item".format(to_obj["name"]),
        #         ItemLimitationWarning,
        #         stacklevel=2,
        #     )

        # TODO
        # Check that from_obj matches the upgrade type to to_obj
        # if not equivalent_upgrade_types(from_obj["name"], to_obj["name"]):
        #     warnings.warn(
        #         "'{}' ({}) cannot be upgraded to '{}' ({}); differing types"
        #         .format(
        #             from_obj["name"], from_obj["type"],
        #             to_obj["name"],   to_obj["type"]
        #         ),
        #         ItemLimitationWarning,
        #         stacklevel=2,
        #     )

        # Check that the index picked is within the correct range
        if not 0 <= index < 24:
            warnings.warn(
                "'index' must be in range [0, 24)", ValueWarning, stacklevel=2
            )

        if self.mappers is None:
            self.mappers = []

        new_mapping = {"from": from_obj, "to": to_obj, "index": index}
        # make sure we get no exact duplicates
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
        """
        try:
            from_obj = signatures.SIGNAL_ID_OR_NONE.validate(from_obj)
            to_obj = signatures.SIGNAL_ID_OR_NONE.validate(to_obj)
            index = signatures.INTEGER_OR_NONE.validate(index)
        except SchemaError as e:
            six.raise_from(DataFormatError, e)

        if index is None:
            # Remove the first occurence of the
            for i, mapping in enumerate(self.mappers):
                if mapping["from"] == from_obj and mapping["to"] == to_obj:
                    self.mappers.pop(i)
        else:
            # Check that the index picked is within the correct range
            if not 0 <= index < 24:
                warnings.warn(
                    "'index' not in range [0, 24)", ValueWarning, stacklevel=2
                )

            mapper = {"from": from_obj, "to": to_obj, "index": index}
            try:
                self.mappers.remove(mapper)
            except ValueError:
                pass

    def to_dict(self):
        # type: () -> dict
        out_dict = copy.deepcopy(self._root)

        if out_dict["settings"] == {}:
            out_dict["settings"] = None  # null

        return {"upgrade_planner": out_dict}
