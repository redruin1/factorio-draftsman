# signals.py

# TODO: automate the collection of signals based on factorio version and mods

from draftsman.signatures import SIGNAL_SCHEMA
from draftsman.errors import InvalidSignalID
from draftsman.signalID import SignalID
from draftsman.data.signals import (
    signal_IDs, item_signals, fluid_signals, virtual_signals
)

from os import path
from typing import Union


class Signal():
    """ Signal object. Holds a SignalID `signal` and a 32 bit int `count`."""
    def __init__(self, id: Union[SignalID, str], count: int):
        self.change_id(id)
        self.count = count

    def change_id(self, id: Union[SignalID, str]) -> None:
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

    def to_dict(self) -> dict:
        """
        Converts Signal class into dictionary. Used in blueprint string 
        conversion.
        """
        return SIGNAL_SCHEMA.validate(
            {"signal": self.id.to_dict(), "count": self.count}
        )

    def __repr__(self):
        return "Signal" + str(self.to_dict())


def get_signal_type(signal_name: str) -> str:
    """
    Returns the type of the signal based on its ID string.
    """
    if signal_name in virtual_signals:
        return "virtual"
    elif signal_name in fluid_signals:
        return "fluid"
    elif signal_name in item_signals:
        return "item"
    else:
        raise InvalidSignalID("'" + str(signal_name) + "'")


def signal_dict(name: str) -> dict:
    return {"name": name, "type": get_signal_type(name)}