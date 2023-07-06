# blueprintable.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
import re

from draftsman.classes.exportable import Exportable
from draftsman.data.signals import signal_dict
from draftsman.error import (
    IncorrectBlueprintTypeError,
    DataFormatError,
)
from draftsman import signatures
from draftsman import utils

from abc import ABCMeta, abstractmethod

from functools import cache
import json
from schema import SchemaError
import six
from typing import Any, Sequence, Union


class Blueprintable(Exportable, metaclass=ABCMeta):
    """
    An abstract base class representing "blueprint-like" objects, such as
    :py:class:`.Blueprint`, :py:class:`.DeconstructionPlanner`,
    :py:class:`.UpgradePlanner`, and :py:class:`.BlueprintBook`.

    All attributes default to keys in the ``self._root`` object, but can (and
    are) overwritten in select circumstances.
    """

    @utils.reissue_warnings
    def __init__(self, root_item, item, init_data, unknown):
        # type: (str, str, Union[str, dict], str) -> None
        """
        Initializes the private ``_root`` data dictionary, as well as setting
        the ``item`` name.
        """
        # Init exportable
        super().__init__()

        # The "root" dict, contains everything inside of this blueprintable
        # Output format is equivalent to:
        # { self._root_item: self._root }

        self._root_item = six.text_type(root_item)
        self._root["item"] = six.text_type(item)

        if init_data is None:
            self.setup()
        elif isinstance(init_data, six.string_types):
            self.load_from_string(init_data, unknown=unknown)
        elif isinstance(init_data, dict):
            self.setup(**init_data[self._root_item], unknown=unknown)
        else:
            raise TypeError(
                "'{}' must be a factorio blueprint string, a dictionary, or None".format(
                    self._root_item
                )
            )

    @utils.reissue_warnings
    def load_from_string(self, string, unknown="error"):
        # type: (str, str) -> None
        """
        Load the :py:class:`.Blueprintable` with the contents of ``string``.

        Raises :py:class:`.DraftsmanWarning` if there are any unrecognized
        keywords in the blueprint string for this particular blueprintable.

        :param string: Factorio-encoded blueprint string.
        :param unknown: TODO

        :exception MalformedBlueprintStringError: If the input string is not
            decodable to a JSON object.
        :exception IncorrectBlueprintTypeError: If the input string is of a
            different type than the base class.
        """
        root = utils.string_to_JSON(string)
        # Ensure that the blueprint string actually points to a blueprint
        if self._root_item not in root:
            raise IncorrectBlueprintTypeError(
                "Expected root keyword '{}', found '{}'; input strings must "
                "match the type of the blueprintable being constructed, or you "
                "can use "
                "`draftsman.blueprintable.get_blueprintable_from_string()` to "
                "generically accept any kind of blueprintable object".format(
                    self._root_item, next(iter(root))
                )
            )

        self.setup(**root[self._root_item], unknown=unknown)

    @abstractmethod
    def setup(self, unknown="error", **kwargs):  # pragma: no coverage
        # type: (str, **dict) -> None
        """
        Setup the Blueprintable's parameters with the input keywords as values.
        Primarily used by the constructor, but can be used at any time to set
        a large number of keys all at once.

        Raises :py:class:`.DraftsmanWarning` if any of the input keywords are
        unrecognized.

        :param unknown: TODO
        :param kwargs: The dict of all keywords to set in the blueprint.

        .. NOTE::

            Calling ``setup`` only sets the specified keys to their values, and
            everything else to either their defaults or ``None``. In other words,
            the effect of calling setup multiple times is not cumulative, but
            rather set to the keys in the last call.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint()
            >>> blueprint.setup(label="test")
            >>> assert blueprint.label == "test"
            >>> test_dict = {"description": "testing..."}
            >>> blueprint.setup(**test_dict)
            >>> assert blueprint.description == "testing..."
            >>> assert blueprint.label == None # Gone!
        """
        pass

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def item(self):
        # type: () -> str
        """
        Always the name of the corresponding Factorio item to this blueprintable
        instance. Read only.

        :type: str

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import (
            ...     Blueprint, DeconstructionPlanner, UpgradePlanner, BlueprintBook
            ... )
            >>> Blueprint().item
            'blueprint'
            >>> DeconstructionPlanner().item
            'deconstruction-planner'
            >>> UpgradePlanner().item
            'upgrade-planner'
            >>> BlueprintBook().item
            'blueprint-book'
        """
        return self._root["item"]

    # =========================================================================

    @property
    def label(self):
        # type: () -> str
        """
        The user given name (title) of the blueprintable.

        :getter: Gets the label, or ``None`` if not set.
        :setter: Sets the label of this object.
        :type: ``str``

        :exception TypeError: When setting ``label`` to something other than
            ``str`` or ``None``.
        """
        return self._root.get("label", None)

    @label.setter
    def label(self, value):
        # type: (str) -> None
        if value is None:
            self._root.pop("label", None)
        else:
            self._root["label"] = value

    # =========================================================================

    @property
    def description(self):
        # type: () -> str
        """
        The description of the blueprintable. Visible when hovering over it when
        inside someone's inventory.

        :getter: Gets the description, or ``None`` if not set.
        :setter: Sets the description of the object. Removes the attribute if
            set to ``None``.
        :type: ``str``

        :exception TypeError: If setting to anything other than a ``str`` or
            ``None``.
        """
        return self._root.get("description", None)

    @description.setter
    def description(self, value):
        # type: (str) -> None
        if value is None:
            self._root.pop("description", None)
        else:
            self._root["description"] = value

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        """
        The visible icons of the blueprintable, shown in as the objects icon.

        Stored as a list of ``ICON`` objects, which are dicts that contain a
        ``SIGNAL_ID`` and an ``index`` key. Icons can be specified in this
        format, or they can be specified more succinctly with a simple list of
        signal names as strings.

        All signal entries must be a valid signal ID. If the input format is a
        list of strings, the index of each item will be it's place in the list
        + 1. A max of 4 icons are permitted.

        :getter: Gets the list if icons, or ``None`` if not set.
        :setter: Sets the icons of the Blueprint. Removes the attribute if set
            to ``None``.
        :type: ``{"index": int, "signal": {"name": str, "type": str}}``

        :exception DataFormatError: If the set value does not match either of
            the specifications above.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint()
            >>> blueprint.icons = ["transport-belt"]
            >>> blueprint.icons
            [{'index': 1, 'signal': {'name': 'transport-belt', 'type': 'item'}}]
        """
        return self._root.get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[Union[dict, str]]) -> None
        if value is None:
            self._root.pop("icons", None)
        else:
            self._root["icons"] = value

    def set_icons(self, *icon_names):
        """
        TODO
        """
        self.icons = [None] * len(icon_names)
        for i, icon in enumerate(icon_names):
            self.icons[i] = {"index": i + 1, "signal": signal_dict(icon)}

    # =========================================================================

    @property
    def version(self):
        # type: () -> int
        """
        The version of Factorio the Blueprint was created in/intended for.

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

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint()
            >>> blueprint.version = (1, 0) # version 1.0.0.0
            >>> assert blueprint.version == 281474976710656
            >>> assert blueprint.version_tuple() == (1, 0, 0, 0)
            >>> assert blueprint.version_string() == "1.0.0.0"
        """
        return self._root.get("version", None)

    @version.setter
    def version(self, value):
        # type: (Union[int, Sequence[int]]) -> None
        if value is None:
            self._root.pop("version", None)
        else:
            self._root["version"] = value

    def set_version(self, major, minor, patch=0, dev_ver=0):
        """
        Convenience function for setting a Blueprintable's version by it's
        component semantic version numbers. Loose wrapper around
        :py:func:`.encode_version`.

        :param major: The major Factorio version.
        :param minor: The minor Factorio version.
        :param patch: The current patch number.
        :param dev_ver: The (internal) development version.
        """
        # TODO: use this method in constructor
        self._root["version"] = utils.encode_version(major, minor, patch, dev_ver)

    # =========================================================================
    # Utility functions
    # =========================================================================

    # TODO
    # def formatted_label(self):
    #     # type: () -> str
    #     """
    #     Returns a formatted string for the console that can be displayed with
    #     the python module ``rich``.

    #     """
    #     if not self.label:
    #         return self.label

    #     formatted_result = self.label
    #     formatted_result = formatted_result.replace("[font=default-bold]", "[bold]")
    #     formatted_result = formatted_result.replace("[/font]", "[/bold]")

    #     formatted_result = re.sub(
    #         r"\[color=(^\]+)\](.*?)\[\/color\]", r"[\1]\2[/\1]", formatted_result
    #     )
    #     # formatted_result = re.sub(r"\[color=(\d+,\d+,\d+)\](.*?)\[\/color\]", r"\[/\]", formatted_result)
    #     # re.sub("\\[[^\\]]+=([^\\]]+)\\]", "\\\\[\\1\\]", formatted_result)

    #     return formatted_result

    def version_tuple(self):
        # type: () -> tuple(int, int, int, int)
        """
        Returns the version of the :py:class:`.Blueprintable` as a 4-length
        tuple.

        :returns: A 4 length tuple in the format ``(major, minor, patch, dev_ver)``.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint({"version": 281474976710656})
            >>> blueprint.version_tuple()
            (1, 0, 0, 0)
        """
        return utils.decode_version(self._root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the :py:class:`.Blueprintable` in human-readable
        string.

        :returns: a ``str`` of 4 version numbers joined by a '.' character.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint({"version": (1, 2, 3)})
            >>> blueprint.version_string()
            '1.2.3.0'
        """
        version_tuple = utils.decode_version(self._root["version"])
        return utils.version_tuple_to_string(version_tuple)

    # def validate(self):
    #     # type: () -> bool
    #     self.label = signatures.Label.validate(self.label)
    #     self.description = signatures.Description.validate(self.description)
    #     self.icons = signatures.Icons.validate(self.icons)
    #     self.version = signatures.Version.validate(self.version)

    #     super().validate()

    def __str__(self):  # pragma: no coverage
        # type: () -> str
        return "<{}>{}".format(
            self.__class__.__name__,
            json.dumps(self.to_dict()[self._root_item], indent=2),
        )
