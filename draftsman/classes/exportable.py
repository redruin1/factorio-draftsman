# exportable.py

from draftsman import utils

from abc import ABCMeta, abstractmethod
from pydantic import BaseModel
from typing import List, Any
import warnings
import pprint  # TODO: think about


class ValidationResult:
    def __init__(self, error_list: List[Exception], warning_list: List[Warning]):
        self.error_list: List[Exception] = error_list
        self.warning_list: List[Warning] = warning_list

    def reissue_all(self):
        for error in self.error_list:
            raise error
        for warning in self.warning_list:
            warnings.warn(warning, stacklevel=2)

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

    def __str__(self):  # pragma: no coverage
        return "ValidationResult{{\n    errors={}, \n    warnings={}\n}}".format(
            pprint.pformat(self.error_list, indent=4),
            pprint.pformat(self.warning_list, indent=4),
        )

    def __repr__(self):  # pragma: no coverage
        return "ValidationResult{{errors={}, warnings={}}}".format(
            self.error_list, self.warning_list
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
        self._root = {}
        self._is_valid = False

    # =========================================================================

    @property
    def is_valid(self):
        """
        TODO
        """
        return self._is_valid

    # =========================================================================

    @abstractmethod
    def validate(self):
        """
        TODO
        """
        # Subsequent objects must implement this method and then call this
        # parent method to cache successful validity
        super().__setattr__("_is_valid", True)

    def inspect(self):
        """
        TODO
        """
        return ValidationResult([], [])

    def to_dict(self) -> dict:
        """
        Returns this object as a dictionary. Intended for getting the precursor
        to a Factorio blueprint string before compression and encoding takes
        place.

        :returns: The ``dict`` representation of this object.
        """
        out_dict = self.__class__.Format.model_construct(  # Performs no validation(!)
            **self._root
        ).model_dump(
            by_alias=True,  # Some attributes are reserved words (type, from,
            # etc.); this resolves that issue
            exclude_none=True,  # Trim if values are None
            exclude_defaults=True,  # Trim if values are defaults
            warnings=False  # Ignore warnings because `model_construct` cannot
            # be made recursive for some asinine reason
        )

        return out_dict

    @classmethod
    def dump_format(cls) -> dict:  # pragma: no coverage
        """
        Returns a JSON schema object that correctly validates this object. Can
        be exported to a JSON string that can be shared and used generically by
        any application that supports JSON schema validation.

        .. see-also::

            https://json-schema.org/

        :returns: A python dictionary containing all the relevant key-value
            pairs, which can be dumped to a string with ``json.dumps``
        """
        # TODO: is this testable?
        return cls.Format.model_json_schema(by_alias=True)

    # =========================================================================

    def __setattr__(self, name, value):
        super().__setattr__("_is_valid", False)
        super().__setattr__(name, value)

    def __setitem__(self, key, value):
        # type: (str, Any) -> None
        self._root[key] = value

    def __getitem__(self, key):
        # type: (str) -> Any
        return self._root[key]

    def __contains__(self, item):
        # type: (str) -> bool
        return item in self._root
