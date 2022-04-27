# blueprintbook.py
# -*- encoding: utf-8 -*-


from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.blueprint import Blueprint
from draftsman.error import IncorrectBlueprintTypeError, DataFormatError
from draftsman import signatures
from draftsman import utils
from draftsman.warning import DraftsmanWarning, IndexWarning

from draftsman.data.signals import signal_dict

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from builtins import int
import copy
from schema import SchemaError
import six
from typing import Union, Sequence
import json
import warnings


class BlueprintableList(MutableSequence):
    """
    List of Blueprintable instances. "Blueprintable" in this context means
    either a Blueprint object or a BlueprintBook, as BlueprintBook objects
    can exist inside other BlueprintBook instances.
    """

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
    Factorio Blueprint Book class. Contains a list of Blueprints as well as some
    of it's own metadata.
    """

    def __init__(self, blueprint_book=None):
        # type: (str, Union[str, dict]) -> None
        """
        Creates a ``BlueprintBook`` class. Will load the data from
        ``blueprint_string`` if provided, otherwise initializes with defaults.

        :param blueprint_string: Either a Factorio-format blueprint string or a
            ``dict`` object with the desired keys in the correct format.
        """

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
        Load the BlueprintBook with the contents of `blueprint_string`. Raises
        ``draftsman.warning.DraftsmanWarning`` if there are any unrecognized
        keywords in the blueprint string.

        :param blueprint_string: Factorio-encoded blueprint string.

        :exception MalformedBlueprintStringError: If the input string is not
            decodable to a JSON object.
        :exception IncorrectBlueprintTypeError: If the input string is of a
            different type than the base class, such as a BlueprintBook.
        """
        root = utils.string_to_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint_book" not in root:
            raise IncorrectBlueprintTypeError

        self.setup(**root["blueprint_book"])

    def setup(self, **kwargs):
        # type: (**dict) -> None
        """
        Setup the BlueprintBook's parameters with the input keywords as values.
        Raises ``draftsman.warning.DraftsmanWarning`` if any of the input
        keywords are unrecognized.

        :param kwargs: The dict of all keywords to set in the blueprint.

        :Example:

        .. code-block:: python

            blueprint = Blueprint()
            blueprint.setup(label="test", description="testing...")
            assert blueprint.label == "test"
            assert blueprint.description == "testing..."
        """
        self.root = dict()

        self.root["item"] = "blueprint-book"
        kwargs.pop("item", None)

        if "label" in kwargs:
            self.label = kwargs.pop("label")

        if "label_color" in kwargs:
            self.label_color = kwargs.pop("label_color")

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
        """
        The BlueprintBook's label (title).

        :getter: Gets the label, or ``None`` if not set.
        :setter: Sets the label of the BlueprintBook.
        :type: ``str``

        :exception TypeError: When setting ``label`` to something other than
            ``str`` or ``None``.
        """
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
        The color of the BlueprintBook's label.

        The ``label_color`` parameter exists in a dict format with the "r", "g",
        "b", and an optional "a" keys. The color can be specified like that, or
        it can be specified more succinctly as a sequence of 3-4 numbers,
        representing the colors in that order.

        The value of each of the numbers (according to Factorio spec) can be
        either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
        <= 1.0, the former range is used, and the latter otherwise. If "a" is
        omitted, it defaults to 1.0 or 255 when imported, depending on the
        range of the other numbers.

        :getter: Gets the color of the label, or ``None`` if not set.
        :setter: Sets the label color of the BlueprintBook.
        :type: ``dict{"r": number, "g": number, "b": number, Optional("a"): number}``

        :exception DataFormatError: If the input ``label_color`` does not match
            the above specification.

        :example:

        .. code-block:: python

            blueprint.label_color = (127, 127, 127)
            print(blueprint.label_color)
            # {'r': 127.0, 'g': 127.0, 'b': 127.0}
        """
        return self.root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self.root.pop("label_color", None)
            return
        try:
            self.root["label_color"] = signatures.COLOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        """
        The icons of the BlueprintBook.

        Stored as a list of ``ICON`` objects, which are dicts that contain a
        ``SIGNAL_ID`` and an ``index`` key. Icons can be specified in this
        format, or they can be specified more succinctly with a simple list of
        signal names as strings.

        All signal entries must be a valid signal id. If the input format is a
        list of strings, the index of each item will be it's place in the list
        + 1. The number of entries cannot exceed 4, or else a
        ``DataFormatError`` is raised.

        :getter: Gets the list if icons, or ``None`` if not set.
        :setter: Sets the icons of the BlueprintBook. Removes the attribute if
            set to ``None``.
        :type: ``dict{"index": int, "signal": {"name": str, "type": str}}``

        :exception DataFormatError: If the set value does not match the
            specification above.
        """
        return self.root.get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[str]) -> None
        if value is None:
            self.root.pop("icons", None)
            return
        try:
            self.root["icons"] = signatures.ICONS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def active_index(self):
        # type: () -> int
        """
        The currently selected Blueprint in the BlueprintBook. Zero-indexed,
        from ``0`` to ``len(blueprint_book.blueprints) - 1``.

        :getter: Gets the index of the currently selected blueprint or blueprint
            book.
        :setter: Sets the index of the currently selected blueprint or blueprint
            book. If the value is ``None``, ``active_index`` defaults to ``0``.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        """
        return self.root.get("active_index", None)

    @active_index.setter
    def active_index(self, value):
        # type: (int) -> None
        if value is None:
            # self.root.pop("active_index", None)
            self.root["active_index"] = 0
        elif isinstance(value, int):
            if not 0 <= value < 65536:
                raise IndexError(
                    "'active_index' ({}) not in range [0, 65536)".format(value)
                )
            elif self.blueprints is not None and value >= len(self.blueprints):
                warnings.warn(
                    "'active_index' ({}) not in range [0, {})".format(
                        value, len(self.blueprints)
                    ),
                    IndexWarning,
                    stacklevel=2,
                )
            self.root["active_index"] = value
        else:
            raise TypeError("'active_index' must be a int or None")

    # =========================================================================

    @property
    def version(self):
        # type: () -> int
        """
        The version of Factorio the BlueprintBook was created in/intended for.

        The Blueprint ``version`` is a 64-bit integer, which is a bitwise-OR
        of four 16-bit numbers. You can interpret this number more clearly by
        decoding it with :py:func:`draftsman.utils.decode_version`, or you can
        use the functions :py:func:`version_tuple` or :py:func:`version_string`
        which will give you a more readable output. This version number defaults
        to the version of Factorio that Draftsman is currently initialized with.

        The version can be set either as said 64-bit int, or a sequence of
        ints, usually a list or tuple, which is then encoded into the combined
        representation. The sequence is defined as:
        ``[major_version, minor_version, patch, development_release]``
        with ``patch`` and ``development_release`` defaulting to 0.

        .. seealso::

            `<https://wiki.factorio.com/Version_string_format>`_

        :getter: Gets the version, or ``None`` if not set.
        :setter: Sets the version of the Blueprint. Removes the attribute if set
            to ``None``.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int``, sequence
            of ``ints``, or ``None``.

        :example:

        .. code-block:: python

            blueprint.version = (1, 0) # version 1.0.0.0
            assert blueprint.version == 281474976710656
            assert blueprint.version_tuple() == (1, 0, 0, 0)
            assert blueprint.version_string() == "1.0.0.0"
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
        The list of Blueprints or BlueprintBooks contained within this
        BlueprintBook.

        :getter: Gets the list of Blueprintables.
        :setter: Sets the list of Blueprintables. The list is initialized empty
            if set to ``None``.
        :type: ``BlueprintableList``

        :exception TypeError: If set to anything other than ``list`` or
            ``None``.
        """
        return self.root.get("blueprints", None)

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
        Returns the version of the Blueprint as a 4-length tuple.

        :returns: a 4 length tuple in the format ``(major, minor, patch, dev_ver)``.
        """
        return utils.decode_version(self.root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the Blueprint in human-readable string.

        :returns: a ``str`` of 4 version numbers joined by a '.' character.
        """
        version_tuple = utils.decode_version(self.root["version"])
        return utils.version_tuple_to_string(version_tuple)

    def to_dict(self):
        # type: () -> dict
        """
        Returns the blueprint as a dictionary. Intended for getting the
        precursor to a Factorio blueprint string before encoding and compression
        takes place.

        :returns: The dict representation of the BlueprintBook.
        """
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
        Returns the Blueprint as an encoded Factorio blueprint string.

        :returns: The zlib-compressed, base-64 encoded string.
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

    # def __repr__(self):  # pragma: no coverage
    #     return "<BlueprintBook>" + json.dumps(self.root, indent=2)
