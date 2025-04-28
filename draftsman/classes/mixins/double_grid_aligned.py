# double_grid_aligned.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.signatures import FloatPosition
from draftsman.warning import GridAlignmentWarning

import math
from pydantic import BaseModel, ValidationInfo, field_validator


class DoubleGridAlignedMixin:
    """
    Makes the Entity issue warnings if set to an odd tile-position coordinate.
    Sets the ``double_grid_aligned`` attribute to ``True``.
    """

    # class Format(BaseModel):
    #     @field_validator("position", check_fields=False)
    #     @classmethod
    #     def ensure_double_grid_aligned(cls, input: FloatPosition, info: ValidationInfo):
    #         if not info.context:
    #             return input
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return input

    #         warning_list: list = info.context["warning_list"]
    #         entity = info.context["object"]
    #         if entity.tile_position.x % 2 == 1 or entity.tile_position.y % 2 == 1:
    #             cast_position = Vector(
    #                 math.floor(entity.tile_position.x / 2) * 2,
    #                 math.floor(entity.tile_position.y / 2) * 2,
    #             )
    #             warning_list.append(
    #                 GridAlignmentWarning(
    #                     "Double-grid aligned entity is not placed along chunk grid; "
    #                     "entity's tile position will be cast from {} to {} when "
    #                     "imported".format(entity.tile_position, cast_position)
    #                 )
    #             )

    #         return input

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True
