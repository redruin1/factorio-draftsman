# cargo_landing_pad.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestFiltersMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)

from draftsman.data.entities import cargo_landing_pads

import attrs


@attrs.define
class CargoLandingPad(
    RequestFiltersMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    A entity on a surface which recieves cargo from space platforms.
    """

    @property
    def similar_entities(self) -> list[str]:
        return cargo_landing_pads

    # =========================================================================

    __hash__ = Entity.__hash__
