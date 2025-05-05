# elevated_curved_rail_b.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode, EIGHT_WAY_DIRECTIONS
from draftsman.utils import get_first

from draftsman.data.entities import elevated_curved_rails_b

import attrs


@attrs.define
class ElevatedCurvedRailB(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    First set of elevated curved rail entities with 2.0 rails. (TODO)
    """

    # class Format(
    #     DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    # ):
    #     model_config = ConfigDict(title="ElevatedCurvedRailB")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(elevated_curved_rails_b),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
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
    #         name,
    #         elevated_curved_rails_b,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return elevated_curved_rails_b

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
