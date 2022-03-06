# signalID.py


class SignalID():
    """ Factorio Signal ID. Type of signal used in circuit networks. """
    def __init__(self, name, type):
        # type: (str, str) -> None
        self.name = name
        self.type = type
        
        # Validate
        #assert SIGNAL_ID_SCHEMA.is_valid({"name": self.name, "type": self.type})

    def to_dict(self):
        # type: () -> dict
        """
        Convert the SignalID to its dict representation. Used when creating 
        blueprint strings.
        """
        return {"name": self.name, "type": self.type}

    def __repr__(self):
        # type: () -> str
        return "SignalID" + str(self.to_dict())