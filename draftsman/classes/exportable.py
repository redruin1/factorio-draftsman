# exportable.py
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import (
    draftsman_converters,
    make_unstructure_function_from_schema,
)
from draftsman.utils import dict_merge
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
import pprint # TODO: find something better


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
        if not isinstance(other, ValidationResult):  # pragma: no coverage
            raise NotImplemented
        self.warning_list += other.warning_list
        self.error_list += other.error_list
        return self

    def __str__(self):  # pragma: no coverage
        return pprint.pformat({"error_list": self.error_list, "warning_list": self.warning_list}, indent=4)

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

    # validate_assignment: ValidationMode = attrs.field(
    #     default=ValidationMode.STRICT,
    #     converter=ValidationMode,
    #     validator=instance_of(ValidationMode),
    #     repr=False,
    #     eq=False,
    #     kw_only=True,
    #     metadata={"omit": True},
    # )
    # """
    # Toggleable flag that indicates whether assignments to this object should
    # be validated, and how. Can be set in the constructor of the entity or
    # changed at any point during runtime. Note that this is on a per-entity
    # basis, so multiple instances of otherwise identical entities can have
    # different validation configurations.
    # """

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
    @conditional(ValidationMode.STRICT)
    def _warn_unrecognized_keys(
        self,
        _: attrs.Attribute,
        value: Optional[dict],
    ):
        """Warns the user if the ``extra_keys`` dict is populated."""
        if value:
            msg = "'{}' object has had the following unrecognized keys:\n{}".format(
                type(self).__name__,
                pprint.pformat(value)
            )
            warnings.warn(UnknownKeywordWarning(msg))

    # =========================================================================

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT
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
        # TODO: I should write my own custom __setattr__ function to every
        # attrs class, such that errors and warnings are passed through as lists
        # and each validator adds itself to that list
        # This will prevent the issues that arise from reissuing warnings, as
        # warnings in Python are just unbelievably cursed in all aspects
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
    def from_dict(
        cls,
        d: dict,
        version: Optional[tuple[int, ...]] = None,
    ) -> Self:
        """
        TODO
        """
        # print("from dict")
        # print(version)
        # import inspect
        # print(
        #     inspect.getsource(draftsman_converters.get_version(version).get_converter().get_structure_hook(cls))
        # )
        if version is None:
            version = mods.versions["base"]

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
        version: Optional[tuple[int, ...]] = None,
        exclude_none: bool = True,
        exclude_defaults: bool = True,
    ) -> dict:
        """
        TODO
        """
        if version is None:
            version = mods.versions["base"]
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

    def __deepcopy__(self, memo: Optional[dict[int, Any]] = {}):
        # Perform the normal deepcopy
        cls = self.__class__
        result = cls.__new__(cls)

        # Make sure we don't copy ourselves multiple times unnecessarily
        memo[id(self)] = result

        # for k, v in self.__dict__.items():
        #     print("key:", k)
        #     print("value:", v)
        #     if k == "_parent":
        #         object.__setattr__(result, "_parent", None)
        #     else:
        #         object.__setattr__(result, k, copy.deepcopy(v, memo))
        # slots = chain.from_iterable(getattr(s, '__slots__', []) for s in self.__class__.__mro__)

        # print(slots)
        # for slot in slots:
        #     print(slot)
        #     setattr(result, slot, copy.deepcopy(getattr(self, slot), memo))

        for attr in attrs.fields(cls):
            # Making the copy of an entity directly "removes" its parent, as there
            # is no guarantee that that cloned entity will actually lie in some
            # EntityCollection
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
        structure_dict = version_data.get_structure_dict(cls)

        def structure_hook(input_dict: dict, _: type):
            res = {}
            for dict_loc, attr_name in structure_dict.items():
                # print(dict_loc, attr_name)
                # if not hasattr(class_attrs, attr_name):
                #     continue
                if attr_name is None:
                    try_pop_location(input_dict, dict_loc)
                    continue

                if isinstance(attr_name, tuple):
                    attr = attr_name[0]
                    custom_handler = attr_name[1]
                    attr_name = attr.alias if attr.alias != attr.name else attr.name
                else:
                    attr = getattr(class_attrs, attr_name)
                    custom_handler = None
                    attr_name = attr.alias if attr.alias != attr.name else attr.name

                value = try_pop_location(input_dict, dict_loc)
                if value is None:
                    continue

                handler = (
                    custom_handler
                    if custom_handler
                    else find_structure_handler(attr, attr.type, converter)
                )
                # import inspect
                # print(inspect.getsource(handler))
                try:
                    res[attr_name] = handler(value, attr.type)
                except Exception as e:
                    # res[attr_name] = value
                    # raise e
                    raise DataFormatError(e)

            # for attr in class_attrs:
            #     # print("attr name:", attr.name, attr.alias)
            #     attr_name = attr.alias if attr.alias != attr.name else attr.name
            #     if attr_name not in structure_dict:
            #         continue
            #     loc = structure_dict[attr_name]

            #     value = try_pop_location(input_dict, loc)
            #     # print(value)
            #     if value is None:
            #         continue
            #     handler = find_structure_handler(attr, attr.type, converter)
            #     if handler is not None:
            #         # import inspect
            #         # print(inspect.getsource(handler))
            #         try:
            #             res[attr_name] = handler(value, attr.type)
            #         except Exception as e:
            #             # res[attr_name] = value
            #             # raise e
            #             raise DataFormatError(e)
            #     else:
            #         res[attr_name] = value

            if input_dict:
                res["extra_keys"] = input_dict

            # print(location_dict)
            # print(res)
            # return res
            return cls(**res)

        return structure_hook

    return factory


def make_exportable_unstructure_factory_func(
    version_tuple: tuple[int, ...], exclude_none: bool, exclude_defaults: bool
):
    def factory(cls, converter):
        version_data = draftsman_converters.get_version(version_tuple)
        unstructure_dict = version_data.get_unstructure_dict(cls, converter)
        # print(cls.__name__)
        # print("unstructure_dict", unstructure_dict)
        parent_hook = make_unstructure_function_from_schema(
            cls,
            converter,
            unstructure_dict,
            exclude_none,
            exclude_defaults,
            version=version_tuple,
        )
        # excluded_keys = version_data.get_excluded_keys(cls)

        def unstructure_hook(inst):
            # import inspect
            # print(inspect.getsource(parent_hook))
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
