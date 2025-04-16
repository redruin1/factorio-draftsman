# validators.py

from draftsman.error import DataFormatError

import attrs

import operator
from typing import Annotated, Any, Union, TYPE_CHECKING, get_origin, get_args

if TYPE_CHECKING:
    from draftsman.classes.exportable import Exportable


def enum_converter(enum):
    def converter(value):
        try:
            return enum(value)
        except ValueError as e:
            raise DataFormatError(e) from None

    return converter


class _AndValidator:
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            for validator in self.validators:
                validator(inst, attr, value, **kwargs)


def and_(*validators):
    return _AndValidator(*validators)


class _OrValidator:
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            messages = []
            for validator in self.validators:
                try:
                    validator(inst, attr, value, **kwargs)
                    return
                except Exception as e:
                    messages.append(str(e))
            msg = "{} did not match any of {}\n\t{}".format(
                repr(value), repr(self.validators),
                "\n\t".join(message for message in messages)
            )
            raise DataFormatError(msg)


def or_(*validators):
    return _OrValidator(*validators)


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
                msg = "{} is not an instance of '{}'".format(
                    repr(value), self.cls.__name__
                )
                raise DataFormatError(msg)
            if self.extra_validator:
                self.extra_validator(inst, attr, value, **kwargs)


def instance_of(cls: type):
    """
    Ensures that a given input matches the type of the given class.
    """
    if get_origin(cls) is Union:
        vs = []
        for u in get_args(cls):
            vs.append(_InstanceOfValidator(u))
        return _OrValidator(*vs)
    else:
        return _InstanceOfValidator(cls)
    

@attrs.define(repr=False, frozen=True, slots=True)
class _NumberValidator:
    bound = attrs.field()
    compare_op = attrs.field()
    compare_func = attrs.field()

    def __call__(self, inst, attr, value, **kwargs):
        mode = kwargs.get("mode", None)
        mode = mode if mode is not None else inst.validate_assignment
        if mode:
            if not self.compare_func(value, self.bound):
                msg = f"'{attr.name}' must be {self.compare_op} {self.bound}: {value}"
                raise DataFormatError(msg)

    def __repr__(self):
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


def le(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number greater than *val*.

    The validator uses `operator.le` to compare the values.

    Args:
        val: Inclusive upper bound for values.

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<=", operator.le)


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


def gt(val):
    """
    A validator that raises `ValueError` if the initializer is called with a
    number smaller or equal to *val*.

    The validator uses `operator.ge` to compare the values.

    Args:
       val: Exclusive lower bound for values

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">", operator.gt)
