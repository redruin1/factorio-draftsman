# signalID.py

from .signatures import SIGNAL_ID_SCHEMA


class SignalID():
    """ Factorio Signal ID. Type of signal used in circuit networks. """
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
        
        # Validate
        #assert SIGNAL_ID_SCHEMA.is_valid({"name": self.name, "type": self.type})

    def to_dict(self):
        """
        Convert the SignalID to its dict representation. Used when creating 
        blueprint strings.
        """
        #return {"name": self.name, "type": self.type}
        return SIGNAL_ID_SCHEMA.validate({"name": self.name, "type": self.type})

    def __repr__(self):
        return "SignalID" + str(self.to_dict())