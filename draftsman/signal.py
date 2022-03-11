# signals.py

from draftsman.error import InvalidSignalError
from draftsman.signatures import SIGNAL

import draftsman.data.signals as signals

from os import path
from typing import Union


class Signal():
    """ 
    Signal object. Holds a str `name`, str `type` and an int `count`.
    """
    def __init__(self, name, count):
        # type: (str, int) -> None
        self.set_name(name)
        self.count = count

    def set_name(self, name):
        # type: (str) -> None
        """
        TODO
        """
        if not isinstance(name, str): 
            raise InvalidSignalError(name)
        
        self.name = name
        self.type = signals.raw[name]

    def set_count(self, count):
        """
        """
        if not isinstance(count, int): 
            raise ValueError("'count' is not int")
        # TODO: warn if count cannot fit in 32bit signed integer
        self.count = count

    def to_dict(self):
        # type: () -> dict
        """
        Converts Signal class into dictionary. Used in blueprint string 
        conversion.
        """
        return {
            "signal": {"name": self.name, "type": self.type}, 
            "count": self.count
        }

    def __str__(self):
        # type: () -> str
        return "Signal" + str(self.to_dict())