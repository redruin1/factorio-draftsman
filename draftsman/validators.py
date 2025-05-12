# validators.py

from draftsman.error import DataFormatError

import attrs

import inspect
import operator
from typing import (
    Annotated,
    Any,
    Literal,
    Optional,
    Union,
    TYPE_CHECKING,
    get_origin,
    get_args,
)
import warnings

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.exportable import Exportable


def conditional(severity):
    """
    Only run the validator if `mode` is greater than a given severity.
    If an `errors` list is provided, mutate that instead of raising.
    """

    def decorator(meth):
        def class_validator(
            self,
            mode=None,
            error_list: Optional[list] = None,
            warning_list: Optional[list] = None,
        ):
            """Validator wrapper for `@classvalidator`."""
            mode = mode if mode is not None else self.validate_assignment
            if mode < severity:
                return

            try:
                with warnings.catch_warnings(record=True) as ws:
                    meth(self)
            except Exception as e:
                if error_list is None:
                    raise e
                else:
                    error_list.append(e)

            if warning_list is None:
                for w in ws:
                    warnings.warn(w.message)
            else:
                warning_list.extend([w.message for w in ws])

        def attr_validator(
            self,
            attr,
            value,
            mode=None,
            error_list: Optional[list] = None,
            warning_list: Optional[list] = None,
        ):
            """Validator wrapper for regular attribute validators."""
            mode = mode if mode is not None else self.validate_assignment
            if mode < severity:
                return

            try:
                with warnings.catch_warnings(record=True) as ws:
                    meth(self, attr, value)
            except Exception as e:
                if error_list is None:
                    raise e
                else:
                    error_list.append(e)

            if warning_list is None:
                for w in ws:
                    warnings.warn(w.message)
            else:
                warning_list.extend([w.message for w in ws])

        sig = inspect.signature(meth)
        if len(sig.parameters) == 1:
            return class_validator
        else:
            return attr_validator

    return decorator


def classvalidator(func):
    """
    Decorator which marks the given function as a validator for the class.
    """
    func.__attrs_class_validator__ = True
    return func


class _AndValidator:
    def __init__(self, validators):
        self._validators = validators

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        for validator in self._validators:
            validator(inst, attr, value, **kwargs)


def and_(*validators):
    vals = []
    for validator in validators:
        vals.extend(
            validator._validators
            if isinstance(validator, _AndValidator)
            else [validator]
        )

    return _AndValidator(tuple(vals))


# We overwrite the "official" `and_` method in attrs with our custom one; the
# only difference being ours can handle **kwargs in the function signature.
# This allows us to use the builtin `@attr.validator` decorator with our custom
# function signatures without remorse, and (hopefully) without breaking compat
# with any other library that happens to use the same attrs features.
import attr

attr._make.and_ = and_


class _OrValidator:
    def __init__(self, validators):
        self.validators = validators

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        messages = []
        for i, validator in enumerate(self.validators):
            try:
                validator(inst, attr, value, **kwargs)
                return
            except DataFormatError as e:
                messages.append(str(e))

        msg = "{} did not match any of {}\n\t{}".format(
            repr(value),
            repr(self.validators),
            "\n\t".join(message for message in messages),
        )
        raise DataFormatError(msg)


def or_(*validators):
    return _OrValidator(validators)


def is_none(inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
    mode = kwargs.get("mode", None)
    mode = mode if mode is not None else inst.validate_assignment
    if mode:  # pragma: no branch
        if not value is None:
            msg = "{} was not None".format(repr(value))
            raise DataFormatError(msg)


class _InstanceOfValidator:
    def __init__(self, cls: type):
        if get_origin(cls) is Annotated:
            args = get_args(cls)
            self.cls = args[0]
            self.extra_validator = args[1]
        else:
            self.cls = cls
            self.extra_validator = None

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            if not isinstance(value, self.cls):
                name = self.cls if isinstance(self.cls, tuple) else self.cls.__name__
                msg = "{} is not an instance of '{}'".format(repr(value), name)
                raise DataFormatError(msg)
            if self.extra_validator:
                self.extra_validator(inst, attr, value, **kwargs)


class _ArgsAreValidator:
    def __init__(self, cls: type):
        # if get_origin(cls) is Annotated:
        #     args = get_args(cls)
        #     self.cls = args[0]
        #     self.extra_validator = args[1]
        # else:
        #     self.cls = cls
        #     self.extra_validator = None
        self.cls = cls

    def __call__(
        self, inst: "Exportable", attr: attrs.Attribute, value: list, **kwargs
    ):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            for i, v in enumerate(value):
                if not isinstance(v, self.cls):
                    name = (
                        self.cls if isinstance(self.cls, tuple) else self.cls.__name__
                    )
                    msg = "Element {} in list ({}) is not an instance of {}".format(
                        i, repr(v), name
                    )
                    raise DataFormatError(msg)
                # if self.extra_validator:
                #     self.extra_validator(inst, attr, value, **kwargs)


def instance_of(cls: type):
    """
    Ensures that a given input matches the type of the given class.
    """
    if get_origin(cls) is Union:
        vs = []
        for u in get_args(cls):
            if u is type(None):  # schizo
                vs.append(is_none)
            else:
                vs.append(_InstanceOfValidator(u))
        return _OrValidator(tuple(vs))
    if get_origin(cls) is list:
        return _AndValidator(
            (_InstanceOfValidator(get_origin(cls)), _ArgsAreValidator(get_args(cls)[0]))
        )
    else:
        return _InstanceOfValidator(cls)


class _OneOfValidator:
    def __init__(self, values):
        self.values = values

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            if value not in self.values:
                msg = "value {} not one of {}".format(repr(value), self.values)
                raise DataFormatError(msg)


def one_of(*values):
    """
    TODO
    """
    if len(values) == 1 and get_origin(values[0]) is Literal:
        return _OneOfValidator(get_args(values[0]))
    else:
        return _OneOfValidator(values)


@attrs.define(repr=False, frozen=True, slots=True)
class _NumberValidator:
    bound = attrs.field()
    compare_op = attrs.field()
    compare_func = attrs.field()

    def __call__(self, inst, attr, value, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            if value is not None and not self.compare_func(value, self.bound):
                msg = f"'{attr.name}' must be {self.compare_op} {self.bound}: {value}"
                raise DataFormatError(msg)

    def __repr__(self):  # pragma: no coverage
        return f"<Validator for x {self.compare_op} {self.bound}>"


def lt(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number larger or equal to *val*.

    The validator uses `operator.lt` to compare the values.

    Args:
        val: Exclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<", operator.lt)


# def le(val):
#     """
#     A validator that raises `ValueError` if the initializer is called with a
#     number greater than *val*.

#     The validator uses `operator.le` to compare the values.

#     Args:
#         val: Inclusive upper bound for values.

#     .. versionadded:: 21.3.0
#     """
#     return _NumberValidator(val, "<=", operator.le)


def ge(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller than *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
        val: Inclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">=", operator.ge)


# def gt(val):
#     """
#     A validator that raises `ValueError` if the initializer is called with a
#     number smaller or equal to *val*.

#     The validator uses `operator.ge` to compare the values.

#     Args:
#        val: Exclusive lower bound for values

#     .. versionadded:: 21.3.0
#     """
#     return _NumberValidator(val, ">", operator.gt)


def try_convert(func):
    """
    Attempt to run the converter function, passing the value through unchanged
    if it fails due to any exception. Under most circumstances, we want the
    validators to actually issue the warnings, and we just want the converters
    to coerce the data into a more accurate form if possible.
    """

    # @functools.wraps(func)
    def try_func(value):
        try:
            return func(value)
        except Exception:
            return value

    return try_func
