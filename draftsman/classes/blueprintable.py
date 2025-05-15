# blueprintable.py

from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.error import IncorrectBlueprintTypeError
from draftsman.signatures import (
    AttrsColor,
    AttrsIcon,
    uint16,
    uint64,
)

# from draftsman.data.signals import signal_dict
from draftsman.serialization import draftsman_converters
from draftsman.utils import (
    encode_version,
    decode_version,
    JSON_to_string,
    string_to_JSON,
    version_tuple_to_string,
)
from draftsman.validators import instance_of, try_convert

from draftsman.data import mods

import attrs

from abc import ABCMeta, abstractmethod

import json
from pydantic import field_validator, ValidationError
from typing import Any, Literal, Optional, Sequence, Union


@attrs.define
class Blueprintable(Exportable, metaclass=ABCMeta):
    """
    An abstract base class representing "blueprint-like" objects, such as
    :py:class:`.Blueprint`, :py:class:`.DeconstructionPlanner`,
    :py:class:`.UpgradePlanner`, and :py:class:`.BlueprintBook`.

    All attributes default to keys in the ``self._root`` object, but can (and
    are) overwritten in select circumstances.
    """

    @classmethod
    def from_string(
        cls,
        string: str,
        # validate: Union[
        #     ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        # ] = ValidationMode.NONE,
    ):
        """
        Creates a :py:class:`.Blueprintable` with the contents of ``string``.

        Raises :py:class:`.UnknownKeywordWarning` if there are any unrecognized
        keywords in the blueprint string for this particular blueprintable.

        :param string: Factorio-encoded blueprint string.

        :exception MalformedBlueprintStringError: If the input string is not
            decodable to a JSON object.
        :exception IncorrectBlueprintTypeError: If the input string is of a
            different type than the base class, such as trying to load the
            string of an upgrade planner into a ``Blueprint`` object.
        """
        json_dict = string_to_JSON(string)
        # Ensure that the blueprint string actually matches the type of the
        # selected class
        root_item = cls.root_item.fget(cls)
        if root_item not in json_dict:
            raise IncorrectBlueprintTypeError(
                "Expected root keyword '{}', found '{}'; input strings must "
                "match the type of the blueprintable being constructed, or you "
                "can use "
                "`draftsman.blueprintable.get_blueprintable_from_string()` to "
                "generically accept any kind of blueprintable object".format(
                    root_item, next(iter(json_dict))
                )
            )
        # Try and get the version from the dictionary, falling back to current
        # environment configuration if not found
        if "version" in json_dict[root_item]:
            version = decode_version(json_dict[root_item]["version"])
        else:
            version = mods.versions["base"]

        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter()
        # import inspect
        # print(inspect.getsource(converter.get_structure_hook(cls)))
        return converter.structure(json_dict, cls)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    @abstractmethod
    def root_item(self) -> str:
        """
        The "root" key of this Blueprintable's dictionary form. For example,
        blueprints have the ``root_item`` key "blueprint":

        ```
        {
            "blueprint": { # <- this is the "root_item"
                ...
            }
        }
        ```

        All keys (except for :py:attr:`index`) are contained within this sub-
        dictionary.
        """
        pass  # pragma: no coverage

    @property
    @abstractmethod
    def item(self) -> str:
        """
        Always the name of the corresponding Factorio item to this blueprintable
        instance. Read only.

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
        pass  # pragma: no coverage

    # =========================================================================

    label: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=instance_of(str),
    )
    """
    The user given name (title) of the blueprintable.

    :exception TypeError: When setting ``label`` to something other than
        ``str`` or ``None``.
    """

    # =========================================================================

    label_color: Optional[AttrsColor] = attrs.field(
        default=None,
        converter=AttrsColor.converter,
        validator=instance_of(Optional[AttrsColor]),
    )
    """
    The color of the Blueprint's label.

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
    :setter: Sets the label color of the ``Blueprint``.

    :exception DataFormatError: If the input ``label_color`` does not match
        the above specification.

    :example:

    .. code-block:: python

        blueprint.label_color = (127, 127, 127)
        print(blueprint.label_color)
        # {'r': 127.0, 'g': 127.0, 'b': 127.0}
    """

    # =========================================================================

    description: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=instance_of(str),
    )
    """
    The description of the blueprintable. Visible when hovering over it when
    inside someone's inventory.

    :exception TypeError: If setting to anything other than a ``str`` or
        ``None``.
    """

    # =========================================================================

    def _icons_converter(value):
        if value is None:
            return []
        elif isinstance(value, Sequence) and not isinstance(value, str):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = AttrsIcon(
                        index=i + 1,
                        signal=elem,
                    )
                else:
                    res[i] = AttrsIcon.converter(elem)
            return res
        else:
            return value

    icons: list[AttrsIcon] = attrs.field(
        factory=list,
        converter=_icons_converter,
        validator=instance_of(list[AttrsIcon]),  # TODO: validators
    )
    """
    The visible icons of the blueprintable, as shown in the icon in
    Factorio's GUI.

    Stored as a list of ``Icon`` objects, which are dicts that contain a
    ``"signal"`` dict and an ``"index"`` key. Icons can be specified in this
    format, or they can be specified more succinctly with a simple list of
    signal names as strings.

    All signal entries must be a valid signal ID. If the input format is a
    list of strings, the index of each item will be it's place in the list
    + 1. A max of 4 icons are permitted.

    :getter: Gets the list if icons, or ``None`` if not set.
    :setter: Sets the icons of the Blueprint. Removes the attribute if set
        to ``None``.

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

    def set_icons(self, *icon_names):
        """
        TODO
        """
        new_icons = [None] * len(icon_names)
        for i, icon in enumerate(icon_names):
            new_icons[i] = AttrsIcon(index=i + 1, signal=icon)
        self.icons = new_icons

    # =========================================================================

    version: uint64 = attrs.field(
        factory=lambda: encode_version(*mods.versions["base"]),
        converter=try_convert(
            lambda value: encode_version(*value)
            if isinstance(value, Sequence)
            else value
        ),
        validator=instance_of(uint64),
        metadata={
            "omit": False,
        },
    )
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

    # =========================================================================

    # TODO: this really probably should be removed, for the same reason that
    # `Entity.entity_number should be removed`; it only really exists for
    # `BlueprintBook.active_index` to work, but that should really probably just
    # be `BlueprintBook.active_blueprint` and have it point directly to the
    # blueprintable
    index: Optional[uint16] = attrs.field(
        default=None, validator=instance_of(Optional[uint16])
    )
    """
    The 0-indexed location of the blueprintable in a parent
    :py:class:`BlueprintBook`. This member is automatically generated if
    omitted, but can be manually set with this attribute. ``index`` has no
    meaning when the blueprintable is not located inside another BlueprintBook.

    :getter: Gets the index of this blueprintable, or ``None`` if not set.
        A blueprintable's index is only generated when exporting with
        :py:meth:`.Blueprintable.to_dict`, so ``index`` will still be ``None``
        until specified otherwise.
    :setter: Sets the index of the :py:class:`.Blueprintable`, or removes it
        if set to ``None``.
    """

    # =========================================================================
    # Utility functions
    # =========================================================================

    # TODO
    # def formatted_label(self) -> str:
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

    def version_tuple(self) -> tuple[uint16, uint16, uint16, uint16]:
        """
        Returns the version of the :py:class:`.Blueprintable` as a 4-length
        tuple.

        :returns: A 4 length tuple in the format ``(major, minor, patch, dev_ver)``.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint(version=281474976710656)
            >>> blueprint.version_tuple()
            (1, 0, 0, 0)
        """
        return decode_version(self.version)

    def version_string(self) -> str:
        """
        Returns the version of the :py:class:`.Blueprintable` in human-readable
        string.

        :returns: a ``str`` of 4 version numbers joined by a '.' character.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import Blueprint
            >>> blueprint = Blueprint(version=(1, 2, 3))
            >>> blueprint.version_string()
            '1.2.3.0'
        """
        return version_tuple_to_string(self.version_tuple())

    # =========================================================================

    def to_string(
        self, version: Optional[tuple[int]] = None
    ) -> str:  # pragma: no coverage
        """
        Returns this object as an encoded Factorio blueprint string.

        :returns: The zlib-compressed, base-64 encoded string.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import (
            ...     Blueprint, DeconstructionPlanner, UpgradePlanner, BlueprintBook
            ... )
            >>> Blueprint({"version": (1, 0)}).to_string()
            '0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDE3sTQ3Mzc0MDM1q60FAHmVE1M='
            >>> DeconstructionPlanner({"version": (1, 0)}).to_string()
            '0eNpdy0EKgCAQAMC/7Nkgw7T8TIQtIdga7tol/HtdunQdmBs2DJlYSg0SMy1nWomwgL+BUSTSzuCppqQgCh7gf6H7goILC78Cfpi0cWZ21unejra1B7C2I9M='
            >>> UpgradePlanner({"version": (1, 0)}).to_string()
            '0eNo1yksKgCAUBdC93LFBhmm5mRB6iGAv8dNE3Hsjz/h0tOSzu+lK0TFThu0oVGtgX2C5xSgQKj2wcy5zCnyUS3gZdjukMuo02shV73qMH4ZxHbs='
            >>> BlueprintBook({"version": (1, 0)}).to_string()
            '0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MTSzNzcwNDcxMzWprAVWGHQI='
        """
        if version is None:
            version = mods.versions["base"]
        return JSON_to_string(self.to_dict(version=version))

    def __str__(self) -> str:  # pragma: no coverage
        return "<{}>{}".format(
            type(self).__name__,
            json.dumps(
                self.to_dict(version=self.version_tuple())[self.root_item], indent=2
            ),
        )

    def __repr__(self) -> str:  # pragma: no coverage
        return "<{}>{}".format(
            type(self).__name__, repr(self.to_dict()[self.root_item])
        )


# TODO: versioning
Blueprintable.add_schema(
    {"properties": {"index": {"oneOf": [{"$ref": "urn:uint16"}, {"type": "null"}]}}}
)

draftsman_converters.add_hook_fns(
    Blueprintable,
    lambda fields: {fields.index.name: "index"},
)
