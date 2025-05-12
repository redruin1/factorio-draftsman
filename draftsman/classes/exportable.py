# exportable.py
from draftsman import __factorio_version_info__
from draftsman.constants import ValidationMode

from draftsman.error import DataFormatError

from abc import ABCMeta, abstractmethod
from pydantic import BaseModel, ValidationError
from typing import Any, List, Literal, Union
import warnings
import pprint  # TODO: think about


def attempt_and_reissue(
    object: Any, format_model: BaseModel, target: Any, name: str, value: Any, **kwargs
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


class Exportable(metaclass=ABCMeta):
    """
    An abstract base class representing an object that has a form within a JSON
    Factorio blueprint string, such as entities, tiles, or entire blueprints
    themselves. Posesses a ``_root`` dictionary which contains it's contents, as
    well as validation utilities.
    """

    class Format(BaseModel):
        pass

    def __init__(self):
        self._root: __class__.Format
        # TODO: hopefully put _root initialization here
        self._is_valid = False
        # Validation assignment is set to "none" on construction since we might
        # not want to validate at this point; validation is performed at the end
        # of construction in the child-most class, if desired
        self._validate_assignment = ValidationMode.NONE

        # TODO: make this a static class property instead of an instance variable
        # (more writing but less memory)
        self._unknown = False

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

    @property
    def validate_assignment(
        self,
    ) -> Union[ValidationMode, Literal["none", "minimum", "strict", "pedantic"]]:
        """
        Toggleable flag that indicates whether assignments to this object should
        be validated, and how. Can be set in the constructor of the entity or
        changed at any point during runtime. Note that this is on a per-entity
        basis, so multiple instances of otherwise identical entities can have
        different validation configurations.

        .. NOTE ::

            Item-assignment (``entity["field"] = obj``) is *never* validated,
            regardless of this parameter. This is mostly a side effect of how
            things work behind the scenes, but it can be used to explicitly
            indicate a "raw" modification that is guaranteed to be cheap and
            will never trigger validation by itself.

        :getter: Gets the assignment mode.
        :setter: Sets the assignment mode. Raises a :py:class:`.DataFormatError`
            if set to an invalid value.
        """
        return self._validate_assignment

    @validate_assignment.setter
    def validate_assignment(self, value):
        self._validate_assignment = ValidationMode(value)

    # =========================================================================

    @property
    def unknown(self) -> bool:
        """
        A read-only flag which indicates whether or not Draftsman recognizes
        this object and thus has a full understanding of it's underlying format.
        If this flag is ``True``, then most validation for this instance is
        disabled, only issuing errors/warnings for issues that Draftsman has
        sufficient information to diagnose.
        """
        return self._unknown

    # =========================================================================

    @abstractmethod
    def validate(self, mode: ValidationMode, force: bool) -> ValidationResult:
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
        # NOTE: Subsequent objects must implement this method and then call this
        # parent method to cache successful validity
        # super().__setattr__("_is_valid", True)
        pass  # pragma: no coverage

    def to_dict(self, exclude_none: bool = True, exclude_defaults: bool = True) -> dict:
        return self._root.model_dump(
            # Some attributes are reserved words ('type', 'from', etc.); this
            # resolves that issue
            by_alias=True,
            # Trim if values are None
            exclude_none=exclude_none,
            # Trim if values are defaults
            exclude_defaults=exclude_defaults,
            # Ignore warnings because we might export a model where the keys are
            # intentionally incorrect
            # Plus there are things like Associations with which we want to
            # preserve when returning this object so that a parent object can
            # handle them
            warnings=False,
        )

    @classmethod
    def json_schema(cls) -> dict:
        """
        Returns a JSON schema object that correctly validates this object. This
        schema can be used with any compliant JSON schema validation library to
        check if a given blueprint string will import into Factorio.

        .. seealso::

            https://json-schema.org/

        :returns: A modern, JSON-schema compliant dictionary with appropriate
            types, ranges, allowed/excluded values, as well as titles and
            descriptions.
        """
        # TODO: should this be tested?
        return cls.Format.model_json_schema(by_alias=True)

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

    def __setitem__(self, key: str, value: Any):
        self._root[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._root[key]

    def __contains__(self, item: str) -> bool:
        return item in self._root
