# blueprintable.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.classes.exportable import Exportable
from draftsman.error import IncorrectBlueprintTypeError
from draftsman.signatures import (
    Color,
    Icon,
    uint16,
    uint64,
)

# from draftsman.data.signals import signal_dict
from draftsman.serialization import draftsman_converters
from draftsman.utils import (
    encode_version,
    decode_version,
    JSON_to_string,
    reissue_warnings,
    string_to_JSON,
    version_tuple_to_string,
)
from draftsman.validators import and_, byte_length, instance_of, try_convert

from draftsman.data import mods

import attrs

from abc import ABCMeta, abstractmethod

import json
from typing import Optional, Sequence


@attrs.define
class Blueprintable(Exportable, metaclass=ABCMeta):
    """
    An abstract base class representing "blueprint-like" objects, such as
    :py:class:`.Blueprint`, :py:class:`.DeconstructionPlanner`,
    :py:class:`.UpgradePlanner`, and :py:class:`.BlueprintBook`.
    """

    @classmethod
    @reissue_warnings
    def from_string(
        cls,
        string: str,
    ):
        """
        Creates a :py:class:`.Blueprintable` with the contents of ``string``.

        Raises :py:class:`.UnknownKeywordWarning` if there are any unrecognized
        keywords in the blueprint string for this particular blueprintable.

        :param string: The Factorio-encoded blueprint string to decode.

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
            version = mods.versions.get("base", DEFAULT_FACTORIO_VERSION)

        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter()
        return converter.structure(json_dict, cls)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    @abstractmethod
    def root_item(self) -> str:
        """
        .. serialized::

            This attribute is imported/exported from blueprint strings.

        The "root" key of this Blueprintable's dictionary form. For example,
        blueprints have the ``root_item`` key "blueprint":

        .. code-block:: python

            {
                "blueprint": { # <- this is the "root_item"
                    ...
                }
            }

        All keys (except for :py:attr:`index`) are contained within this sub-
        dictionary.
        """
        pass  # pragma: no coverage

    @property
    @abstractmethod
    def item(self) -> str:
        """
        .. serialized::

            This attribute is imported/exported from blueprint strings.

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
        validator=and_(instance_of(str), byte_length(200)),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The user given name (title) of the blueprintable.
    """

    # =========================================================================

    label_color: Optional[Color] = attrs.field(
        default=None,
        converter=Color.converter,
        validator=instance_of(Optional[Color]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The :py:class:`.Color` of the Blueprint's label.
    """

    # =========================================================================

    description: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=and_(instance_of(str), byte_length(500)),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The description of the blueprintable. Visible when hovering over it when
    inside someone's inventory. Has a maximum size of 500 bytes.
    """

    # =========================================================================

    def _icons_converter(value):
        # This function is slow, but since icons will never be greater than 4
        # items long it should be fine
        if isinstance(value, Sequence) and not isinstance(value, str):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = Icon(index=i, signal=elem)
                else:
                    res[i] = elem
            return res
        else:
            return value

    icons: list[Icon] = attrs.field(
        factory=list,
        converter=_icons_converter,
        validator=instance_of(list[Icon]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The visible icons of the blueprintable, as shown in the icon in
    Factorio's GUI. A max of 4 :py:class:`.Icon` s are permitted.

    Icons can also be specified more succinctly as a simple list of signal names:

    .. doctest::

        >>> from draftsman.blueprintable import Blueprint
        >>> blueprint = Blueprint()
        >>> blueprint.icons = ["transport-belt"]
        >>> blueprint.icons
        [Icon(index=0, signal=SignalID(name='transport-belt', type='item', quality='normal'))]
    """

    # =========================================================================

    # TODO: why bother having the integer representation at all? Just have
    # `version` point to a tuple instead of `version_tuple`, and do the custom
    # encoding
    # If people really want the integer, they can just use `encode_version`
    version: uint64 = attrs.field(
        factory=lambda: encode_version(
            *mods.versions.get("base", DEFAULT_FACTORIO_VERSION)
        ),
        converter=try_convert(
            lambda value: (
                encode_version(*value) if isinstance(value, Sequence) else value
            )
        ),
        validator=instance_of(uint64),
        metadata={
            "omit": False,
        },
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The version of Factorio the Blueprint was created in/intended for.

    The Blueprint ``version`` is a 64-bit integer, which is a bitwise-OR
    of four 16-bit numbers. You can interpret this number more clearly by
    decoding it with :py:func:`draftsman.utils.decode_version`, or you can
    use the functions :py:func:`version_tuple` or :py:func:`version_string`
    which will give you a more readable output. This version number defaults
    to the version of Factorio of Draftsman's environment.

    The version can be set either a 64-bit int in the format above, or as a 
    sequence of ints (usually a list or tuple) which is then encoded into the 
    combined representation. The sequence is defined as:
    ``[major_version, minor_version, patch, development_release]``
    with ``patch`` and ``development_release`` defaulting to 0.

    :example:

    .. doctest::

        >>> from draftsman.blueprintable import Blueprint
        >>> blueprint = Blueprint()
        >>> blueprint.version = (1, 0) # version 1.0.0.0
        >>> assert blueprint.version == 281474976710656
        >>> assert blueprint.version_tuple() == (1, 0, 0, 0)
        >>> assert blueprint.version_string() == "1.0.0.0"

    .. seealso::

        `<https://wiki.factorio.com/Version_string_format>`_
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
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The location of the blueprintable in a parent :py:class:`.BlueprintBook`. 
    This member is automatically generated if omitted, but can be manually set 
    with this attribute. This attribute has no meaning when the blueprintable is 
    not located inside another blueprint book.
    """

    # =========================================================================
    # Utility functions
    # =========================================================================

    # TODO
    # @abstractmethod
    # def migrate_to(self, target_version: tuple[int, ...] | None):
    #     """
    #     Takes this particular Blueprintable and attempts to migrate it to the
    #     specified version, mostly renaming entity/tile/recipe names.

    #     TODO
    #     """
    #     pass  # pragma: no coverage

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
            >>> Blueprint(version=(1, 0)).to_string()
            '0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDE3sTQ3Mzc0MDM1q60FAHmVE1M='
            >>> DeconstructionPlanner(version=(1, 0)).to_string()
            '0eNqrVkpJTc7PKy4pKk0uyczPiy/ISczLSy1SsqpWyixJzVWyQlOgC1Ogo1SWWlQMFFGyMrIwNDE3sTQ3Mzc0MDM1q60FAHp9Hf0='
            >>> UpgradePlanner(version=(1, 0)).to_string()
            '0eNqrViotSC9KTEmNL8hJzMtLLVKyqlbKLEnNVbKCyejCZHSUylKLijPz85SsjCwMTcxNLM3NzA0NzEzNamsBqdIX5Q=='
            >>> BlueprintBook(version=(1, 0)).to_string()
            '0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJTKUouKM/PzlKyMLAxNzE0szc3MDQ3MTM10lBKTSzLLUuMz81JSK5SsDGprATINHQI='
        """
        if version is None:
            version = mods.versions.get("base", DEFAULT_FACTORIO_VERSION)
        return JSON_to_string(self.to_dict(version=version))

    def __str__(self) -> str:  # pragma: no coverage
        return "<{}>{}".format(
            type(self).__name__,
            json.dumps(
                self.to_dict(version=self.version_tuple())[self.root_item], indent=2
            ),
        )

    def __repr__(self) -> str:  # pragma: no coverage
        return "{}(**{})".format(
            type(self).__name__, repr(self.to_dict()[self.root_item])
        )


draftsman_converters.add_hook_fns(
    Blueprintable,
    lambda fields: {fields.index.name: "index"},
)
