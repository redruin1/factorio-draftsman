# cargo_landing_pad.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestFiltersMixin,
    CargoHubModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import cargo_landing_pads

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class CargoLandingPad(
    RequestFiltersMixin,
    CargoHubModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    A entity on a surface which recieves cargo from space platforms.
    """

    # class Format(
    #     RequestFiltersMixin.Format,
    #     CargoHubModeOfOperationMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CargoHubModeOfOperationMixin.ControlFormat, DraftsmanBaseModel
    #     ):
    #         pass

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="CargoLandingPad")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(cargo_landing_pads),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     control_behavior: Optional[Format.ControlBehavior] = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name=name,
    #         similar_entities=cargo_landing_pads,
    #         position=position,
    #         tile_position=tile_position,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return cargo_landing_pads

    # =========================================================================

    __hash__ = Entity.__hash__
