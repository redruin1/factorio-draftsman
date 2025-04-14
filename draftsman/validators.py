# validators.py

from draftsman.error import DataFormatError

import attrs

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from draftsman.classes.exportable import Exportable


class _InstanceOfValidator:
    def __init__(self, cls: type):
        self.cls = cls

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        if inst.validate_assignment or kwargs.get("mode", None):
            if not isinstance(value, self.cls):
                msg = "{} is not an instance of '{}'".format(repr(value), self.cls.__name__)
                raise DataFormatError(msg)


def instance_of(cls: type):
    """
    Ensures that a given input matches the type of the given class.
    """
    return _InstanceOfValidator(cls)


class _AndValidator:
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, inst: "Exportable", attr: attrs.Attribute, value: Any, **kwargs):
        if inst.validate_assignment or kwargs.get("mode", None):
            for validator in self.validators:
                validator(inst, attr, value, **kwargs)

def and_(*validators):
    return _AndValidator(*validators)
