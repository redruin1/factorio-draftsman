# exportable.py
from draftsman import __factorio_version_info__
from draftsman.constants import ValidationMode
from draftsman.serialization import (
    draftsman_converters,
    make_unstructure_function_from_schema,
)
from draftsman.utils import dict_merge

from draftsman.error import DataFormatError
from draftsman import validators
from draftsman.warning import UnknownKeywordWarning

import attrs
from attr._make import _CountingAttr
import cattrs
from cattrs.gen._shared import find_structure_handler

from abc import ABCMeta, abstractmethod
import copy
from functools import wraps
from pydantic import BaseModel, ValidationError
from typing import Any, List, Literal, Optional, Union
from typing_extensions import Self
import warnings
import pprint  # TODO: think about


def convert_to_countingattr(attr):
    """
    Convert an `Attribute` instance to an equivalent `_CountingAttr` instance.
    """
    return attrs.field(
        **{
            slot: getattr(attr, slot)
            for slot in attr.__slots__
            if slot not in {"name", "eq_key", "order_key", "inherited"}
        }
    )


def custom_define(field_order: list[str], **kwargs):
    import inspect

    @wraps(attrs.define)
    def wrapper(cls):
        # Pre-attrs definition
        these = {}
        for field_name in field_order:
            field = getattr(cls, field_name, attrs.field())

            # Grabbing fields from already `@define`d classes return memberdescriptors
            if inspect.ismemberdescriptor(field):
                # If so, grab it using attrs plumbing and convert it to _CountingAttr
                field = getattr(attrs.fields(cls), field_name)
                field = convert_to_countingattr(field)
            # If it's not a _CountingAttr, then it must be the default value
            elif not isinstance(field, _CountingAttr):
                field = attrs.field(default=field)

            these[field_name] = field

        # # Post-attrs definition
        # original_init = res.__init__

        # @wraps(original_init)
        # def new_init(*args, **kwargs):
        #     kwargs.pop("entity_number", None)
        #     original_init(*args, **kwargs)

        # cls.__init__ = new_init

        return attrs.define(cls, these=these, **kwargs)

    return wrapper


def attempt_and_reissue(
    object: Any, format_model: Any, target: Any, name: str, value: Any, **kwargs
):
    """
    Helper function that normalizes assignment validation
    """
    context = {
        "mode": object.validate_assignment,
        "object": object,
        "warning_list": [],
        "assignment": True,
        "environment_version": __factorio_version_info__,
        **kwargs,
    }
    if object.validate_assignment == ValidationMode.NONE:
        context["construction"] = True
    try:
        result = format_model.__pydantic_validator__.validate_assignment(
            target,
            name,
            value,
            strict=False,  # TODO: disallow any weird string -> int / string -> bool conversions
            context=context,
        )
    except ValidationError as e:
        raise DataFormatError(e) from None
    for warning in context["warning_list"]:
        warnings.warn(warning, stacklevel=4)
    # result = result.model_dump(warnings=False)
    # return result[name]
    return getattr(result, name)


def apply_assignment(
    object: "Exportable",
    format_model: BaseModel,
    target: BaseModel,
    name: str,
    value: Any,
    **kwargs
):
    """
    TODO
    """
    context = {
        "mode": ValidationMode.NONE,
        "object": object,
        "warning_list": [],
        "assignment": True,
        "construction": True,
        **kwargs,
    }
    # try:
    result = format_model.__pydantic_validator__.validate_assignment(
        target,
        name,
        value,
        strict=True,  # TODO: disallow any weird string -> int / string -> bool conversions
        context=context,
    )
    # except ValidationError as e:
    #     raise DataFormatError(e) from None
    # for warning in context["warning_list"]:
    #     warnings.warn(warning, stacklevel=4)
    return getattr(result, name)


def test_replace_me(
    object: "Exportable",
    format_model: BaseModel,
    target: BaseModel,
    name: str,
    value: Any,
    mode: ValidationMode,
    **kwargs
):
    """
    Attempts to coerce a input value to a particular Pydantic model format, and
    run validation at the same time if requested by the caller. Utility function
    to increase code reuse.

    The input value is expected to be in a standard JSON format, what you would
    expect a regular input to look like. Any shorthand formats should be handled
    *before* passing to this function.

    If the passed in mode is `ValidationMode.NONE`, then this function attempts
    to just coerce the input to a Pydantic BaseModel using the "construction"
    key. Because using this key should generate no errors or warnings, the
    original value will just be returned when it is indeterminate. Under any
    other passed in `mode`, the validation suite is run corresponding to that
    mode.
    """
    context = {
        "mode": mode,
        "object": object,
        "warning_list": [],
        "assignment": True,  # Do not revalidate the entire object; just this attr
        "environment_version": __factorio_version_info__,
        **kwargs,
    }
    # Functions check for presence, not value; so we only add it when necessary
    if mode is ValidationMode.NONE:
        context["construction"] = True

    try:
        result = format_model.__pydantic_validator__.validate_assignment(
            target,
            name,
            value,
            strict=True,  # TODO: disallow any weird str to int or str to bool conversions
            context=context,
        )
    except ValidationError as e:
        raise DataFormatError(e) from None
    for warning in context["warning_list"]:
        warnings.warn(warning, stacklevel=4)
    target[name] = getattr(result, name)


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
                type(self.error_list[i]) != type(other.error_list[i])
                or self.error_list[i].args != other.error_list[i].args
            ):
                return False
        for i in range(len(self.warning_list)):
            if (
                type(self.warning_list[i]) != type(other.warning_list[i])
                or self.warning_list[i].args != other.warning_list[i].args
            ):
                return False
        return True

    def __iadd__(self, other):
        if not isinstance(other, ValidationResult):
            raise NotImplemented
        self.warning_list += other.warning_list
        self.error_list += other.error_list
        return self

    def __str__(self):  # pragma: no coverage
        return "ValidationResult{{\n    errors={},\n    warnings={}\n}}".format(
            pprint.pformat(self.error_list, indent=4),
            pprint.pformat(self.warning_list, indent=4),
        )

    def __repr__(self):  # pragma: no coverage
        return "ValidationResult{{errors={}, warnings={}}}".format(
            repr(self.error_list), repr(self.warning_list)
        )


@attrs.define(slots=False)
class Exportable:
    """
    An abstract base class representing an object that has a form within a
    Factorio blueprint string, such as entities, tiles, or entire blueprints
    themselves.
    """

    # _is_valid: bool = attrs.field(default=False, init=False)
    # validation: ValidationMode = attrs.field(
    #     default=ValidationMode.NONE,
    #     repr=False,
    #     eq=False,
    #     metadata={"omit": True, "location": None},
    # )

    # def __init__(self):
    #     self._root: __class__.Format
    #     # TODO: hopefully put _root initialization here
    #     self._is_valid = False
    #     # Validation assignment is set to "none" on construction since we might
    #     # not want to validate at this point; validation is performed at the end
    #     # of construction in the child-most class, if desired
    #     self._validate_assignment = ValidationMode.NONE

    #     # TODO: make this a static class property instead of an instance variable
    #     # (more writing but less memory)
    #     self._unknown = False

    # =========================================================================

    # TODO
    # @property
    # def is_valid(self) -> bool:
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

    validate_assignment: ValidationMode = attrs.field(
        default=ValidationMode.STRICT,
        converter=ValidationMode,
        validator=validators.instance_of(ValidationMode),
        repr=False,
        kw_only=True,
        metadata={"omit": True},
    )
    """
    Toggleable flag that indicates whether assignments to this object should
    be validated, and how. Can be set in the constructor of the entity or
    changed at any point during runtime. Note that this is on a per-entity
    basis, so multiple instances of otherwise identical entities can have
    different validation configurations.
    """

    # @property
    # def validate_assignment(
    #     self,
    # ) -> Union[ValidationMode, Literal["none", "minimum", "strict", "pedantic"]]:
    #     """
    #     Toggleable flag that indicates whether assignments to this object should
    #     be validated, and how. Can be set in the constructor of the entity or
    #     changed at any point during runtime. Note that this is on a per-entity
    #     basis, so multiple instances of otherwise identical entities can have
    #     different validation configurations.

    #     .. NOTE ::

    #         Item-assignment (``entity["field"] = obj``) is *never* validated,
    #         regardless of this parameter. This is mostly a side effect of how
    #         things work behind the scenes, but it can be used to explicitly
    #         indicate a "raw" modification that is guaranteed to be cheap and
    #         will never trigger validation by itself.

    #     :getter: Gets the assignment mode.
    #     :setter: Sets the assignment mode. Raises a :py:class:`.DataFormatError`
    #         if set to an invalid value.
    #     """
    #     return self._validate_assignment

    # @validate_assignment.setter
    # def validate_assignment(self, value):
    #     self._validate_assignment = ValidationMode(value)

    # =========================================================================

    extra_keys: Optional[dict[Any, Any]] = attrs.field(
        default=None, kw_only=True, metadata={"omit": True}
    )
    """
    Any additional keys that are not recognized by Draftsman when loading from
    a raw JSON dictionary end up as keys in this attribute. Under normal 
    circumstances, this field should always remain ``None``, indicating that all 
    fields provided were properly translated into the internal Python class. 
    
    This attribute allows you to have "raw-like" access to the input/output dict,
    should you wish to add additional keys when distributing serialized 
    blueprint strings. Any keys that remain in this dict will be respected on 
    output, so you can populate this dictionary with custom keys (beyond what 
    you could do with ``tags``) and they will be combined on output, meaning 
    round-trip import-export cycles are stable:

    TODO: round-trip example

    The structure of input keys are preserved, meaning you may have to recurse
    through keys to find the unknown data:

    TODO: control_behavior example
    """

    @extra_keys.validator
    def _warn_unrecognized_keys(
        self, _, value: Optional[dict], mode: Optional[ValidationMode] = None
    ):
        """Warns the user if the ``extra_keys`` dict is populated."""
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.STRICT and value:  # is not empty:
            msg = "'{}' object has no attribute(s) {}; allowed fields are {}".format(
                type(self).__name__,
                list(value.keys()),
                [
                    attr.name
                    for attr in attrs.fields(type(self))
                    if not attr.name.startswith("_")
                ],
            )
            warnings.warn(UnknownKeywordWarning(msg))

    # =========================================================================

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        """
        Validates the called object against it's known format.
        Method that attempts to first coerce the object into a known form, and
        then checks the values of its attributes for correctness. If unable to
        do so, this function raises :py:class:`.DataFormatError`. Otherwise,
        no errors are raised and :py:attr:`.is_valid` is set to ``True``.

        :example:

        .. doctest::

            >>> from draftsman.entity import Container
            >>> from draftsman.error import DataFormatError
            >>> c = Container("wooden-chest", validate_assignment="none")
            >>> c.bar = "incorrect"
            >>> try:
            ...     c.validate().reissue_all()
            ... except DataFormatError as e:
            ...     print("wrong!")
            wrong!

        :param mode: How strict to be when valiating the object, corresponding
            to the number and type of errors and warnings returned.
        :param force: Whether or not to ignore this entity's `is_valid` flag and
            attempt to revalidate anyway.

        :returns: A :py:class:`ValidationResult` object containing the
            corresponding errors and warnings.
        """
        mode = ValidationMode(mode)
        res = ValidationResult([], [])
        for a in attrs.fields(self.__class__):
            v = a.validator
            if v is not None:
                try:
                    with warnings.catch_warnings(record=True) as w:
                        v(self, a, getattr(self, a.name), mode=mode)
                    for warning in w:
                        res.warning_list.append(warning.category(warning.message))
                except Exception as e:
                    res.error_list.append(e)
        return res

    @classmethod
    def from_dict(
        cls,
        d: dict,
        version: tuple[int, ...] = __factorio_version_info__,
        validation: ValidationMode = ValidationMode.NONE,
    ) -> Self:
        """
        TODO
        """
        # print("from dict")
        # print(version)
        # import inspect
        # print(
        #     inspect.getsource(draftsman_converters.get(version).get_structure_hook(cls))
        # )
        version_info = draftsman_converters.get_version(version)
        return version_info.get_converter().structure(
            copy.deepcopy(d), cls
        )  # TODO: move deepcopy internal
        # kwargs = version_info.get_converter().structure(copy.deepcopy(d), cls)
        # res = cls(**kwargs, validate_assignment=ValidationMode.NONE)
        # if validation:
        #     res.validate(mode=validation).reissue_all()
        # res.validate_assignment = validation
        # return res

    def to_dict(
        self,
        version: tuple[int, ...] = __factorio_version_info__,
        exclude_none: bool = True,
        exclude_defaults: bool = True,
    ) -> dict:
        """
        TODO
        """
        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter(exclude_none, exclude_defaults)
        # print(converter)
        # print(converter.omit_if_default)
        # import inspect
        # print(inspect.getsource(converter.get_unstructure_hook(type(self))))
        # print(getattr(attrs.fields(type(self)), "always_on").default)
        # defaults = {field.name: field.default for field in attrs.fields(type(self))}
        # print(defaults)
        # print(getattr(self, "color"))
        # return {
        #     k: v for k, v in converter.unstructure(self, type(self)).items()
        #     if not ((v is None and exclude_none) or (getattr(self, k) == defaults[k] and exclude_defaults))
        # }
        return converter.unstructure(self)
        # return self._root.model_dump(
        #     # Some attributes are reserved words ('type', 'from', etc.); this
        #     # resolves that issue
        #     by_alias=True,
        #     # Trim if values are None
        #     exclude_none=exclude_none,
        #     # Trim if values are defaults
        #     exclude_defaults=exclude_defaults,
        #     # Ignore warnings because we might export a model where the keys are
        #     # intentionally incorrect
        #     # Plus there are things like Associations with which we want to
        #     # preserve when returning this object so that a parent object can
        #     # handle them
        #     warnings=False,
        # )

    @classmethod
    def json_schema(
        cls, version: tuple[int, ...] = __factorio_version_info__
    ) -> dict[str, Any]:
        """
        Returns a JSON schema object that correctly validates this object. This
        schema can be used with any compliant JSON schema validation library to
        check if a given blueprint dict will import into Factorio as an
        additional layer of validation.

        :param version: The Factorio version for which you would like the schema
            to validate. Diff-ing these schemas between versions allows you to
            view changes in the blueprint format across time.

        .. seealso::

            https://json-schema.org/

        :returns: A modern, JSON-schema compliant dictionary with appropriate
            types, ranges, allowed/excluded values, as well as titles and
            descriptions.
        """
        # TODO: should this be tested?
        # TODO: should this schema be "resolved", meaning all references are
        # flattened out? If not, how should somebody actually use the urls
        # in practice, since they're all locally hosted?
        # return cls.Format.model_json_schema(by_alias=True)
        return draftsman_converters.get_version(version).get_schema(cls)

    # TODO
    # @classmethod
    # def get_format(cls, indent: int=2) -> str:
    #     """
    #     Produces a pretty string representation of ``meth:json_schema``. Work in
    #     progress.

    #     :returns: A formatted string that can be output to stdout or file.
    #     """
    #     return json.dumps(cls.json_schema(), indent=indent)

    # =========================================================================

    # TODO
    # def __setattr__(self, name, value):
    #     super().__setattr__("_is_valid", False)
    #     super().__setattr__(name, value)

    # def __setitem__(self, key: str, value: Any):
    #     self._root[key] = value

    # def __getitem__(self, key: str) -> Any:
    #     return self._root[key]

    # def __contains__(self, item: str) -> bool:
    #     return item in self._root


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
        location_dict = version_data.get_location_dict(cls)

        def structure_hook(input_dict: dict, _: type):
            res = {}
            for attr in class_attrs:
                # print("attr name:", attr.name)
                if attr.name not in location_dict:
                    continue
                loc = location_dict[attr.name]

                value = try_pop_location(input_dict, loc)
                # print(value)
                if value is None:
                    continue
                handler = find_structure_handler(attr, attr.type, converter)
                if handler is not None:
                    # import inspect
                    # print(inspect.getsource(handler))
                    try:
                        res[attr.name] = handler(value, attr.type)
                    except Exception as e:
                        raise DataFormatError(e)
                else:
                    res[attr.name] = value

            if input_dict:
                res["extra_keys"] = input_dict

            # print(location_dict)
            # print(res)
            # return res
            return cls(**res, validate_assignment=ValidationMode.NONE)

        return structure_hook

    return factory


def make_exportable_unstructure_factory_func(
    version_tuple: tuple[int, ...], exclude_none: bool, exclude_defaults: bool
):
    def factory(cls, converter):
        version_data = draftsman_converters.get_version(version_tuple)
        location_dict = version_data.get_location_dict(cls)
        parent_hook = make_unstructure_function_from_schema(
            cls, converter, location_dict, exclude_none, exclude_defaults
        )
        excluded_keys = version_data.get_excluded_keys(cls)

        def unstructure_hook(inst):
            res = parent_hook(inst)
            # We want to preserve round-trip consistency, even with keys we
            # don't use/recognize
            if inst.extra_keys:
                dict_merge(res, inst.extra_keys)
            # Certain keys we do always want to exclude in certain circumstances
            # (such as objects like "connections" on Factorio >= 2.0)
            for key in excluded_keys:
                if key in res:
                    del res[key]
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
