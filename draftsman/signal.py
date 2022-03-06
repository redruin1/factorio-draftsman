# signals.py

# TODO: automate the collection of signals based on factorio version and mods

from draftsman.signatures import SIGNAL
from draftsman.errors import InvalidSignalID
from draftsman.signalID import SignalID
from draftsman.data.signals import signal_IDs


from os import path
from typing import Union


class Signal():
    """ Signal object. Holds a SignalID `signal` and an int `count`."""
    def __init__(self, id, count):
        # type: (Union[SignalID, str], int) -> None
        self.change_id(id)
        self.count = count

    def change_id(self, id):
        # type: (Union[SignalID, str]) -> None
        """
        Swaps the ID of the signal to something else and changes aliases.
        """
        if isinstance(id, str):
            self.id = signal_IDs[id]
        elif isinstance(id, SignalID):
            self.id = id
        else:
            raise InvalidSignalID("'" + str(id) + "'")
        
        #self.name = self.id.name
        #self.type= self.id.type

    def to_dict(self):
        # type: () -> dict
        """
        Converts Signal class into dictionary. Used in blueprint string 
        conversion.
        """
        return SIGNAL.validate(
            {"signal": self.id.to_dict(), "count": self.count}
        )

    def __repr__(self):
        # type: () -> str
        return "Signal" + str(self.to_dict())