# circuit_read_resource.py

from draftsman import signatures
from draftsman.constants import MiningDrillReadMode


class CircuitReadResourceMixin(object): # (ControlBehaviorMixin)
    """
    TODO
    """
    @property
    def read_resources(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("circuit_read_resources", None)

    @read_resources.setter
    def read_resources(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_read_resources", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_resources"] = value
        else:
            raise TypeError("'read_resources' must be a bool or None")

    # =========================================================================

    @property
    def read_mode(self):
        # type: () -> MiningDrillReadMode
        """
        TODO
        """
        return self.control_behavior.get("circuit_resource_read_mode", None)

    @read_mode.setter
    def read_mode(self, value):
        # type: (MiningDrillReadMode) -> None
        if value is None:
            self.control_behavior.pop("circuit_resource_read_mode", None)
        elif isinstance(value, int):
            self.control_behavior["circuit_resource_read_mode"] = value
        else:
            raise TypeError(
                "'read_mode' must be an instance of int or None"
            )