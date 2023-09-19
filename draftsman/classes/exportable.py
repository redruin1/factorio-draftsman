# exportable.py

from draftsman import utils

from abc import ABCMeta, abstractmethod
from pydantic import BaseModel
from typing import List, Any
import warnings
import pprint  # TODO: think about


class ValidationResult:
    """
    TODO
    """
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
        self._root = {}
        self._is_valid = False

    # =========================================================================

    @property
    def is_valid(self):
        """
        Read-only attribute that indicates whether or not this object is 
        validated. If this attribute is true, you can assume that all component 
        attributes of this object are formatted correctly and value tolerant. 
        Validity is lost anytime any attribute of a valid object is altered, and 
        gained when :py:meth:`.validate` is called:

        .. example::

            >>> from draftsman.entity import Container
            >>> c = Container("wooden-chest")
            >>> c.is_valid
            False
            >>> c.validate()
            >>> c.is_valid
            True
            >>> c.bar = 10  # Even though 10 is a valid value, validate() must 
            >>> c.is_valid  # be called again for draftsman to know this
            False

        Read only.
        """
        return self._is_valid

    # =========================================================================

    @abstractmethod
    def validate(self):
        """
        Method that attempts to first coerce the object into a known form, and
        then checks the values of its attributes for correctness. If unable to
        do so, this function raises :py:error:`.DataFormatError`. Otherwise,
        no errors are raised and :py:attr:`.is_valid` is set to ``True``.

        .. example::

            >>> from draftsman.entity import Container
            >>> from draftsman.error import DataFormatError
            >>> c = Container("wooden-chest")
            >>> c.bar = "incorrect"
            >>> try:
            ...     c.validate()
            ... except DataFormatError as e:
            ...     print("wrong! {}", e)
            wrong!

        :raises:
        """
        # NOTE: Subsequent objects must implement this method and then call this
        # parent method to cache successful validity
        super().__setattr__("_is_valid", True)

    def inspect(self):
        """
        Inspects

        :returns: A :py:class:`.ValidationResult` object, containing any found
            errors or warnings pertaining to this object.
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
    def json_schema(cls) -> dict:  # pragma: no coverage
        """
        Returns a JSON schema object that correctly validates this object. Can
        be exported to a JSON string that can be shared and used generically by
        any application that supports JSON schema validation.

        .. see-also::

            https://json-schema.org/

        :returns: A python dictionary containing all the relevant key-value
            pairs, which can be dumped to a string with ``json.dumps``.
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
