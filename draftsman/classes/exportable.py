# exportable.py

from draftsman import utils

from abc import ABCMeta, abstractmethod
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
    TODO
    """

    def __init__(self):
        self._root = {}
        self._is_valid = False

    def __setattr__(self, name, value):
        super().__setattr__("_is_valid", False)
        super().__setattr__(name, value)

    @property
    def is_valid(self):
        """
        TODO
        """
        return self._is_valid

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

    @abstractmethod
    def to_dict(self):  # pragma: no coverage
        # type: () -> dict
        """
        Returns this object as a dictionary. Intended for getting the precursor
        to a Factorio blueprint string before encoding and compression takes
        place.

        :returns: The ``dict`` representation of this object.
        """
        pass

    def to_string(self):  # pragma: no coverage
        # type: () -> str
        """
        Returns this object as an encoded Factorio blueprint string.

        :returns: The zlib-compressed, base-64 encoded string.

        :example:

        .. doctest::

            >>> from draftsman.blueprintable import (
            ...     Blueprint, DeconstructionPlanner, UpgradePlanner, BlueprintBook
            ... )
            >>> Blueprint({"version": (1, 0)}).to_string()
            '0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDE3sTQ3Mzc0MDM1q60FAHmVE1M='
            >>> DeconstructionPlanner({"version": (1, 0)}).to_string()
            '0eNpdy0EKgCAQAMC/7Nkgw7T8TIQtIdga7tol/HtdunQdmBs2DJlYSg0SMy1nWomwgL+BUSTSzuCppqQgCh7gf6H7goILC78Cfpi0cWZ21unejra1B7C2I9M='
            >>> UpgradePlanner({"version": (1, 0)}).to_string()
            '0eNo1yksKgCAUBdC93LFBhmm5mRB6iGAv8dNE3Hsjz/h0tOSzu+lK0TFThu0oVGtgX2C5xSgQKj2wcy5zCnyUS3gZdjukMuo02shV73qMH4ZxHbs='
            >>> BlueprintBook({"version": (1, 0)}).to_string()
            '0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MTSzNzcwNDcxMzWprAVWGHQI='
        """
        # TODO: add options to compress/canoncialize blueprints before export
        # (though should that happen on a per-blueprintable basis? And what about non-Blueprint strings, like upgrade planners?)
        return utils.JSON_to_string(self.to_dict())

    def __setitem__(self, key, value):
        # type: (str, Any) -> None
        self._root[key] = value

    def __getitem__(self, key):
        # type: (str) -> Any
        return self._root[key]

    def __contains__(self, item):
        # type: (str) -> bool
        return item in self._root
