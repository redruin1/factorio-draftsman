# constant_combinator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import constant_combinators


class ConstantCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                         DirectionalMixin, Entity):
    """
    TODO: maybe keep signal filters internally as an array of Signal objects,
    and then use Signal.to_dict() during that stage?
    """
    def __init__(self, name: str = constant_combinators[0], **kwargs):
        if name not in constant_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(ConstantCombinator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_signal(self, index: int, signal: str, count: int = 0) -> None:
        """
        """
        # Check validity before modifying self
        index = signatures.INTEGER.validate(index)
        signal = signatures.SIGNAL_ID.validate(signal)
        count = signatures.INTEGER.validate(count)

        if "filters" not in self.control_behavior:
            self.control_behavior["filters"] = []
        
        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.control_behavior["filters"]):
            if index + 1 == filter["index"]: # Index already exists in the list
                if signal is None: # Delete the entry
                    del self.control_behavior["filters"][i]
                else: # Set the new value
                    self.control_behavior["filters"][i] = {
                        "index": index + 1,"signal": signal, "count": count
                    }
                return

        # If no entry with the same index was found
        self.control_behavior["filters"].append({
            "index": index + 1, "signal": signal, "count": count
        })

    def set_signals(self, signals: list) -> None:
        """
        """
        signals = signatures.SIGNAL_FILTERS.validate(signals)

        if signals is None:
            self.control_behavior.pop("filters", None)
        else:
            self.control_behavior["filters"] = signals

    # def get_signal(self, index: int) -> Signal:
    #     """
    #     """
    #     return None # TODO