# valve.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import valves

import attrs


@attrs.define
class Valve(DirectionalMixin, Entity):
    """
    A pipe that may or may not admit fluid to pass through it based on some
    threshold.
    """

    @property
    def similar_entities(self) -> list[str]:
        return valves

    @property
    def threshold(self) -> float | None:
        """
        Returns the fluid saturation needed for this valve to pass its fluid.
        This value is lies within the range [0.0, 1.0], where 1.0 is 100% full.
        """
        return (self.prototype if self.prototype else {"threshold": None}).get(
            "threshold", 0.0
        )

    # =========================================================================

    __hash__ = Entity.__hash__
