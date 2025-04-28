# land_mine.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import land_mines

import attrs


@attrs.define
class LandMine(Entity):
    """
    An entity that explodes when in proximity to another force.
    """

    # class Format(Entity.Format):
    #     model_config = ConfigDict(title="LandMine")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(land_mines),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
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
    #         land_mines,
    #         position=position,
    #         tile_position=tile_position,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return land_mines

    # =========================================================================

    __hash__ = Entity.__hash__
