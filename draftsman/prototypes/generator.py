# generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import generators

import attrs


@fix_incorrect_pre_init
@attrs.define
class Generator(DirectionalMixin, Entity):
    """
    An entity that converts a fluid (usually steam) to electricity.
    """

    # class Format(DirectionalMixin.Format, Entity.Format):
    #     model_config = ConfigDict(title="Generator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(generators),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         generators,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return generators

    # =========================================================================

    __hash__ = Entity.__hash__
