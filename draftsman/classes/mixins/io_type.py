# io_type.py

from draftsman import signatures


class IOTypeMixin(object):
    """
    Gives an entity a Input/Output type. Used on underground belts and loaders.
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(IOTypeMixin, self).__init__(name, similar_entities, **kwargs)
        
        self.io_type = "input" # Default
        if "io_type" in kwargs:
            self.io_type = kwargs["io_type"]
            self.unused_args.pop("io_type")
        self._add_export(
            "io_type", 
            lambda x: x is not None and x != "input",
            lambda k, v: ("type", v)
        )
    
    # =========================================================================

    @property
    def io_type(self):
        # type: () -> str
        """
        Input-output type of the entity. Can be either 'input', 'output', or 
        None.
        TODO
        """
        return self._io_type

    @io_type.setter
    def io_type(self, value):
        # type: (str) -> None
        if value not in {"input", "output", None}:
            raise TypeError(
                "'io_type' must be 'input', 'output' or None"
            )
        self._io_type = value