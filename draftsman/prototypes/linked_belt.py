# linked_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import linked_belts

import attrs


@fix_incorrect_pre_init
@attrs.define
class LinkedBelt(DirectionalMixin, Entity):  # TODO: finish
    """
    A belt object that can transfer items over any distance, regardless of
    constraint, as long as the two are paired together.

    .. WARNING::

        Functionally, currently unimplemented. Need to analyze how mods use this
        entity, as I can't seem to figure out the example one in the game.
    """

    # class Format(DirectionalMixin.Format, Entity.Format):
    #     model_config = ConfigDict(title="LinkedBelt")

    # def __init__(
    #     self,
    #     name: str = get_first(linked_belts),
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
    #         linked_belts,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return linked_belts

    # =========================================================================

    __hash__ = Entity.__hash__
