# exportable.py
from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import (
    draftsman_converters,
    make_unstructure_function_from_schema,
)
from draftsman.utils import dict_merge, reissue_warnings
from draftsman.validators import conditional
from draftsman.warning import UnknownKeywordWarning

from draftsman.data import mods

import attrs
import cattrs
from cattrs.gen._shared import find_structure_handler

import copy
from typing import Any, List, Optional
from typing_extensions import Self
import warnings
import pprint  # TODO: find something better


class ValidationResult:
    """
    Helper object used to contain errors and warnings issued from
    :py:meth:`.Exportable.validate`.
    """

    def __init__(self, error_list: List[Exception], warning_list: List[Warning]):
        self.error_list: List[Exception] = error_list
        self.warning_list: List[Warning] = warning_list

    def reissue_all(self, stacklevel=2):
        for error in self.error_list:
            raise error
        for warning in self.warning_list:
            warnings.warn(warning, stacklevel=stacklevel)

    def __eq__(self, other):  # pragma: no coverage
        # Primarily for test suite.
        if not isinstance(other, ValidationResult):
            return False
        if len(self.error_list) != len(other.error_list) or len(
            self.warning_list
        ) != len(other.warning_list):
            return False
        for i in range(len(self.error_list)):
            if (
                type(self.error_list[i]) is not type(other.error_list[i])
                or self.error_list[i].args != other.error_list[i].args
            ):
                return False
        for i in range(len(self.warning_list)):
            if (
                type(self.warning_list[i]) is not type(other.warning_list[i])
                or self.warning_list[i].args != other.warning_list[i].args
            ):
                return False
        return True

    def __iadd__(self, other):
        if not isinstance(other, ValidationResult):  # pragma: no coverage
            raise NotImplementedError
        self.warning_list += other.warning_list
        self.error_list += other.error_list
        return self

    def __str__(self):  # pragma: no coverage
        return pprint.pformat(
            {"error_list": self.error_list, "warning_list": self.warning_list}, indent=4
        )

    def __repr__(self):  # pragma: no coverage
        return "ValidationResult(errors={}, warnings={})".format(
            repr(self.error_list), repr(self.warning_list)
        )


@attrs.define(slots=False)
class Exportable:
    """
    An abstract base class representing an object that has a form within a
    Factorio blueprint string, such as entities, tiles, or entire blueprints
    themselves.
    """

    # def __new__(cls, *args, **kwargs):
    #     return super().__new__(cls)

    # @property
    # def is_valid(self) -> bool: # TODO
    #     """
    #     Read-only attribute that indicates whether or not this object is
    #     validated. If this attribute is true, you can assume that all component
    #     attributes of this object are formatted correctly and value tolerant.
    #     Validity is lost anytime any attribute of a valid object is altered, and
    #     gained when :py:meth:`.validate` is called:

    #     .. doctest::

    #         >>> from draftsman.entity import Container
    #         >>> c = Container("wooden-chest")
    #         >>> c.is_valid
    #         False

    #     Read only.
    #     """
    #     return self._is_valid

    # =========================================================================

    extra_keys: Optional[dict[str, Any]] = attrs.field(
        default=None, kw_only=True, repr=False, metadata={"omit": True}
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Any additional keys that are not recognized by Draftsman when loading from
    a raw JSON dictionary end up as keys in this attribute. Under normal 
    circumstances, this field should always remain ``None``, indicating that all 
    fields provided were properly translated into the internal Python format. 
    
    If there are any values in ``extra_keys`` after being imported from a raw
    JSON dictionary, then (left alone) these values will also be exported back
    into an output JSON dictionary in order to keep import-export cycles stable.
    A side effect of this is that users can use this attribute to *add* 
    additional fields that will end up in the output string, primarily for 
    custom metadata that can be read by other tools::

        >>> input_dict = {
        ...    "name": "wooden-chest",
        ...    "position": {"x": 0.5, "y": 0.5},
        ...    "unknown_key": "blah"
        ... }
        >>> container = Container.from_dict(input_dict)
        >>> container.extra_keys
        {"unknown_key": "blah"}
        >>> container.extra_keys["custom"] = "data"
        >>> container.to_dict()
        {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "unknown_key": "blah",
            "custom": "data"
        }

    The structure of input keys are preserved, meaning you may have to recurse
    through keys to find the unknown data::

        >>> input_dict = {
        ...     "name": "wooden-chest",
        ...     "position": {"x": 0.5, "y": 0.5},
        ...     "nested": {
        ...         "dictionary": "value"
        ...     }
        ... }
        >>> container = Container.from_dict(input_dict)
        >>> container.extra_keys
        {"nested": {"dictionary": "value"}}

    .. NOTE::

        While Draftsman makes an effort to preserve keys that it doesn't 
        recognize, Factorio itself makes no such effort - so if you create a 
        blueprint string with custom metadata and then import it into the game, 
        that additional data will be stripped and cannot be retrieved when 
        exporting a new string from the game.
    """

    @extra_keys.validator
    @conditional(ValidationMode.STRICT)
    def _warn_unrecognized_keys(
        self,
        _: attrs.Attribute,
        value: Optional[dict],
    ):
        """Warns the user if the ``extra_keys`` dict is populated."""
        if value:
            msg = "'{}' object has had the following unrecognized keys:\n{}".format(
                type(self).__name__, pprint.pformat(value)
            )
            warnings.warn(UnknownKeywordWarning(msg))

    # =========================================================================

    @classmethod
    def converter(cls, value: Any):
        """
        Try to convert the given ``value`` to an instance of this particular
        class. By default, it assumes value is a ``dict`` whose keywords map
        to attributes of this class.

        :meta private:
        """
        try:
            return cls(**value)
        except TypeError:
            return value

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT
    ) -> ValidationResult:
        """
        Validates the called object against it's known format.

        :example:

        .. doctest::

            >>> import draftsman
            >>> from draftsman.constants import ValidationMode
            >>> from draftsman.entity import Container
            >>> from draftsman.error import DataFormatError
            >>> c = Container("wooden-chest")
            >>> with draftsman.validators.set_mode(ValidationMode.DISABLED):
            ...     c.bar = "incorrect"
            >>> try:
            ...     c.validate().reissue_all()
            ... except DataFormatError as e:
            ...     print("wrong!")
            wrong!

        :param mode: How strict to be when valiating the object, corresponding
            to the number and type of errors and warnings returned.

        :returns: A :py:class:`.ValidationResult` object, which contains all
            errors and warnings from the validation pass.
        """
        mode = ValidationMode(mode)
        res = ValidationResult([], [])
        for a in attrs.fields(self.__class__):
            v = a.validator
            if v is not None:
                v(
                    self,
                    a,
                    getattr(self, a.name),
                    mode=mode,
                    error_list=res.error_list,
                    warning_list=res.warning_list,
                )
        return res

    @classmethod
    @reissue_warnings
    def from_dict(
        cls,
        d: dict,
        version: Optional[tuple[int, ...]] = None,
    ) -> Self:
        """
        Attempts to construct a new instance of this class from a Python
        dictionary in JSON format.

        :param d: The dictionary to interpret.
        :param version: The Factorio version that the input data is compliant
            with.

            The given version tuple will automatically attempt to grab the
            closest applicable converter - meaning that specifying a
            version of ``(1, 1, 96)`` will use the 1.0 converter, and a
            version of ``(2, 0, 32)`` will use the 2.0 converter.

            If no version is provided, it will default to current environment's
            Factorio version, or to :py:data:`draftsman.DEFAULT_FACTORIO_VERSION`
            if unable to read the current environment.
        """
        if version is None:
            version = mods.versions.get("base", DEFAULT_FACTORIO_VERSION)

        version_info = draftsman_converters.get_version(version)
        return version_info.get_converter().structure(
            copy.deepcopy(d), cls
        )  # TODO: remove deepcopy here, use locals in structure func instead

    def to_dict(
        self,
        version: Optional[tuple[int, ...]] = None,
        exclude_none: bool = True,
        exclude_defaults: bool = True,
    ) -> dict:
        """
        Export this object to a JSON dictionary, usually directly prior to
        encoding into the compressed blueprint string format.

        :param version: Which Factorio version format this entity should be
            exported with. The same Draftsman object can be converted to many
            version-specific output dictionaries, each of which may have
            different structures.

            The given version tuple will automatically attempt to grab the
            closest applicable converter - meaning that specifying a
            version of ``(1, 1, 96)`` will use the 1.0 converter, and a
            version of ``(2, 0, 32)`` will use the 2.0 converter.

            If no version is provided, it will default to current environment's
            Factorio version, or to :py:data:`draftsman.DEFAULT_FACTORIO_VERSION`
            if unable to read the current environment.
        :param exclude_none: Whether or not ``None`` properties should be
            omitted from the output string. For certain properties this option
            has no effect, as they either must always be present or never
            be present if ``None``.
        :param exclude_defaults: Whether or not to exclude properties that are
            equivalent to their default values. Including these values in the
            generated output is redundant as Factorio will populate them
            automatically, but it is useful to disable for debug/illustation
            purposes.
        """
        if version is None:
            version = mods.versions.get("base", DEFAULT_FACTORIO_VERSION)
        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter(exclude_none, exclude_defaults)
        return converter.unstructure(self)

    # =========================================================================

    def __deepcopy__(self, memo: Optional[dict[int, Any]] = {}):
        # Perform the normal deepcopy
        cls = self.__class__
        result = cls.__new__(cls)

        # Make sure we don't copy ourselves multiple times unnecessarily
        memo[id(self)] = result

        for attr in attrs.fields(cls):
            # Making the copy of an entity directly "removes" its parent, as there
            # is no guarantee that that cloned entity will actually lie in some
            # Collection
            if "deepcopy_func" in attr.metadata:
                object.__setattr__(
                    result,
                    attr.name,
                    attr.metadata["deepcopy_func"](getattr(self, attr.name), memo),
                )
            else:
                object.__setattr__(
                    result, attr.name, copy.deepcopy(getattr(self, attr.name), memo)
                )

        return result


def make_exportable_structure_factory_func(
    version_tuple: tuple[int, ...], exclude_none: bool, exclude_defaults: bool
):
    def factory(cls: type, converter: cattrs.Converter):
        def try_pop_location(subdict, loc):
            """
            Traverse loc and try to pop that item, as well as any subdicts that
            become empty in the process.
            """
            if loc is None:
                return None
            if len(loc) == 1:
                try:
                    return subdict.pop(loc[0], None)
                except AttributeError:
                    return None
            if loc[0] not in subdict:
                return None
            result = try_pop_location(subdict[loc[0]], loc[1:])
            if subdict[loc[0]] == {}:
                subdict.pop(loc[0])
            return result

        class_attrs = attrs.fields(cls)
        version_data = draftsman_converters.get_version(version_tuple)
        structure_dict = version_data.get_structure_dict(cls, converter)

        def structure_hook(input_dict: dict, _: type):
            inst = cls.__new__(cls)

            print(input_dict)

            init_args = {}
            for source_loc, dest_loc in structure_dict.items():
                # If the destination is None, that's us telling the structure
                # function to ignore that particular entry
                if dest_loc is None:
                    try_pop_location(input_dict, source_loc)
                    continue

                print(source_loc, dest_loc)

                if isinstance(dest_loc, dict):
                    custom_handler = dest_loc.get("handler", None)
                    attr = dest_loc["attr"]
                    attr_name = dest_loc["name"]
                    attr_type = dest_loc["type"]
                elif isinstance(dest_loc, tuple):
                    attr = dest_loc[0]
                    custom_handler = dest_loc[1]
                    attr_name = attr.alias if attr.alias != attr.name else attr.name
                    attr_type = attr.type
                else:
                    attr = getattr(class_attrs, dest_loc)
                    custom_handler = None
                    attr_name = attr.alias if attr.alias != attr.name else attr.name
                    attr_type = attr.type

                # print(source_loc, dest_loc)
                # print(attr)
                # print(attr_name)
                # print(attr_type)
                # print(custom_handler)

                value = try_pop_location(input_dict, source_loc)
                # No value means nothing to do
                if value is None:
                    continue

                # Grab the appropriate structure handler
                handler = (
                    custom_handler
                    if custom_handler is not None
                    else find_structure_handler(attr, attr_type, converter)
                )
                # print(handler)
                try:
                    if custom_handler:
                        init_args[attr_name] = handler(value, attr_type, inst)
                    else:
                        init_args[attr_name] = handler(value, attr_type)
                except Exception as e:
                    raise DataFormatError(e)

            if input_dict:
                init_args["extra_keys"] = input_dict

            print(init_args)

            inst.__init__(**init_args)
            return inst

        return structure_hook

    return factory


def make_exportable_unstructure_factory_func(
    version_tuple: tuple[int, ...], exclude_none: bool, exclude_defaults: bool
):
    def factory(cls, converter):
        version_data = draftsman_converters.get_version(version_tuple)
        unstructure_dict = version_data.get_unstructure_dict(cls, converter)
        parent_hook = make_unstructure_function_from_schema(
            cls,
            converter,
            unstructure_dict,
            exclude_none,
            exclude_defaults,
            version=version_tuple,
        )

        def unstructure_hook(inst):
            # TODO: should be wrapped in a try block with a better error message
            res = parent_hook(inst)
            # We want to preserve round-trip consistency, even with keys we
            # don't use/recognize
            if inst.extra_keys:
                dict_merge(res, inst.extra_keys)
            return res

        return unstructure_hook

    return factory


for version_tuple, version in draftsman_converters.versions.items():
    for exclude_config, converter in version.converters.items():
        # Technically don't have to do this for *every* structure, but...
        converter.register_structure_hook_factory(
            lambda cls: issubclass(cls, Exportable),
            make_exportable_structure_factory_func(version_tuple, *exclude_config),
        )
        converter.register_unstructure_hook_factory(
            lambda cls: issubclass(cls, Exportable),
            make_exportable_unstructure_factory_func(version_tuple, *exclude_config),
        )
