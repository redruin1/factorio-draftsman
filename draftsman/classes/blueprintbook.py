# blueprintbook.py
# -*- encoding: utf-8 -*-

# TODO: Complete!

from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.blueprint import Blueprint
from draftsman.error import IncorrectBlueprintTypeError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import DraftsmanWarning

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from builtins import int
import copy
from schema import SchemaError
from typing import Union, Sequence
import json
import warnings


class BlueprintableList(MutableSequence):
    def __init__(self, initlist=None):
        # type: (list[Blueprint]) -> None
        self.data = []
        if initlist is not None:
            for elem in initlist:
                self.append(elem)

    def insert(self, idx, value):
        # type: (int, Union[Blueprint, BlueprintBook]) -> None
        # Make sure the blueprintable is valid
        self.check_blueprintable(value)

        self.data.insert(idx, value)

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        # type: (int, Union[Blueprint, BlueprintBook]) -> None
        # Make sure the blueprintable is valid
        self.check_blueprintable(value)

        self.data[idx] = value

    def __delitem__(self, idx):
        del self.data[idx]

    def __len__(self):
        return len(self.data)

    def check_blueprintable(self, blueprintable):
        if not isinstance(blueprintable, Blueprint) and not isinstance(
            blueprintable, BlueprintBook
        ):
            raise TypeError(
                "Entry into BlueprintableList must be either a Blueprint or a "
                "BlueprintBook"
            )


class BlueprintBook(object):
    """
    Factorio Blueprint Book.
    """

    def __init__(self, blueprint_book=None):
        # type: (str, list[Blueprint, BlueprintBook]) -> None

        if blueprint_book is None:
            self.setup()
        elif isinstance(blueprint_book, str):
            self.load_from_string(blueprint_book)
        elif isinstance(blueprint_book, dict):
            self.setup(**blueprint_book)
        else:
            raise TypeError(
                "'blueprint_book' must be a factorio blueprint "
                "string, a file object, a dictionary, or None"
            )

    def load_from_string(self, blueprint_string):
        # type: (str) -> None
        """
        Load the BlueprintBook with the contents of `blueprint_string`.

        Args:
            blueprint_string (str): Factorio-encoded blueprint string.
        """
        root = utils.string_to_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint_book" not in root:
            raise IncorrectBlueprintTypeError

        self.setup(**root["blueprint_book"])

    def setup(self, **kwargs):
        # type: (**dict) -> None
        """
        Sets up the default attributes for a BlueprintBook.
        """
        self.root = dict()

        self.root["item"] = "blueprint-book"
        kwargs.pop("item", None)

        self.active_index = 0
        if "active_index" in kwargs:
            self.active_index = kwargs.pop("active_index")

        if "version" in kwargs:
            self.version = kwargs.pop("version")
        else:
            self.version = utils.encode_version(*__factorio_version_info__)

        if "blueprints" in kwargs:
            self.root["blueprints"] = BlueprintableList(kwargs.pop("blueprints"))
        else:
            self.root["blueprints"] = BlueprintableList()

        # Issue warnings for any keyword not recognized by BlueprintBook
        for unused_arg in kwargs:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================
    # BlueprintBook properties
    # =========================================================================

    @property
    def label(self):
        # type: () -> None
        """ """
        return self.root.get("label", None)

    @label.setter
    def label(self, value):
        # type: (str) -> None
        if value is None:
            self.root.pop("label", None)
        elif isinstance(value, str):
            self.root["label"] = value
        else:
            raise TypeError("`label` must be a string")

    # =========================================================================

    @property
    def label_color(self):
        # type: () -> dict
        """
        Sets the color of the Blueprint's label (title).

        Args:
            r (float): Red component, 0.0 - 1.0
            g (float): Green component, 0.0 - 1.0
            b (float): Blue component, 0.0 - 1.0
            a (float): Alpha component, 0.0 - 1.0

        Raises:
            SchemaError if any of the values cannot be resolved to floats
        """
        return self.root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self.root.pop("label_color", None)
        else:
            try:
                self.root["label_color"] = signatures.COLOR.validate(value)
            except SchemaError:
                # TODO: more verbose
                raise TypeError("Invalid Color format")

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        """
        Sets the icon or icons associated with the blueprint.

        Args:
            signals: List of signal names to set as icons

        Raises:
            InvalidSignalID if any signal is not a string or unknown
        """
        return self.root.get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[str]) -> None
        if value is None:
            self.root.pop("icons", None)
            return

        self.root["icons"] = []
        for i, signal in enumerate(value):
            if isinstance(signal, str):
                out = {"index": i + 1}
                out["signal"] = utils.signal_dict(signal)
            elif isinstance(signal, dict):
                try:
                    out = signatures.ICON.validate(signal)
                except SchemaError:
                    # TODO: more verbose
                    raise ValueError("Incorrect icon format")
            else:
                raise TypeError("Icon entries must be either a str or a dict")

            self.root["icons"].append(out)

    # =========================================================================

    @property
    def active_index(self):
        # type: () -> int
        """
        TODO
        """
        return self.root.get("active_index", None)

    @active_index.setter
    def active_index(self, value):
        # type: (int) -> None
        if value is None:
            # self.root.pop("active_index", None)
            self.root["active_index"] = 0
        elif isinstance(value, int):
            # if value > len(self.blueprints):
            #     warnings.warn(
            #         "'active_index' out of bounds"

            #     )
            self.root["active_index"] = value
        else:
            raise TypeError("'active_index' must be a int or None")

    # =========================================================================

    @property
    def version(self):
        # type: () -> int
        """
        The version of the Blueprint.
        """
        return self.root.get("version", None)

    @version.setter
    def version(self, value):
        # type: (Union[int, Sequence[int]]) -> None
        if value is None:
            self.root.pop("version", None)
        elif isinstance(value, int):
            self.root["version"] = value
        elif isinstance(value, Sequence):
            self.root["version"] = utils.encode_version(*value)
        else:
            raise TypeError("'version' must be an int, sequence of ints or None")

    # =========================================================================

    @property
    def blueprints(self):
        # type: () -> BlueprintableList
        """
        TODO
        """
        return self.root["blueprints"]

    @blueprints.setter
    def blueprints(self, value):
        if value is None:
            self.root["blueprints"] = BlueprintableList()
        elif isinstance(value, list):
            self.root["blueprints"] = BlueprintableList(value)
        else:
            raise TypeError("'blueprints' must be a list or None")

    # =========================================================================
    # Utility functions
    # =========================================================================

    def version_tuple(self):
        # type: () -> tuple(int, int, int, int)
        """
        Returns the version of the BlueprintBook as a 4-length tuple.
        """
        return utils.decode_version(self.root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the BlueprintBook in human-readable string.
        """
        version_tuple = utils.decode_version(self.root["version"])
        return utils.version_tuple_to_string(version_tuple)

    def to_dict(self):
        # type: () -> dict
        # Get the root dicts from each blueprint and insert them into blueprints
        out_dict = copy.deepcopy(self.root)

        out_dict["blueprints"] = []
        for i, blueprintable in enumerate(self.blueprints):
            blueprintable_entry = blueprintable.to_dict()
            blueprintable_entry["index"] = i
            out_dict["blueprints"].append(blueprintable_entry)

        if len(out_dict["blueprints"]) == 0:
            del out_dict["blueprints"]

        return {"blueprint_book": out_dict}

    def to_string(self):  # pragma: no coverage
        # type: () -> str
        """
        Returns the BlueprintBook as a Factorio blueprint string.
        """
        return utils.JSON_to_string(self.to_dict())

    def __setitem__(self, key, value):
        self.root[key] = value

    def __getitem__(self, key):
        return self.root[key]

    def __str__(self):  # pragma: no coverage
        return "<BlueprintBook>" + json.dumps(
            self.to_dict()["blueprint_book"], indent=2
        )

    def __repr__(self):  # pragma: no coverage
        return "<BlueprintBook>" + json.dumps(self.root, indent=2)
