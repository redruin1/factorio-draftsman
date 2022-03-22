# double_grid_aligned.py

from draftsman.warning import RailAlignmentWarning

import math
import warnings


class DoubleGridAlignedMixin(object):
    """
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(DoubleGridAlignedMixin, self).__init__(
            name, similar_entities, **kwargs
        )

        self._double_grid_aligned = True

        # Technically redundant, but we 
        if "position" in kwargs:
            self.position = kwargs["position"]

    # =========================================================================

    def set_absolute_position(self, x, y):
        # type: (float, float) -> None
        """
        Overwritten
        """
        super(DoubleGridAlignedMixin, self).set_absolute_position(x, y)

        # if the grid alignment is off, warn the user
        if self.tile_position[0] % 2 == 1 or self.tile_position[1] % 2 == 1:
            cast_position = [math.floor(self.tile_position[0] / 2) * 2,
                             math.floor(self.tile_position[1] / 2) * 2]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported"
                .format(self.tile_position, cast_position),
                RailAlignmentWarning,
                stacklevel = 2
            )

    def set_tile_position(self, x, y):
        # type: (int, int) -> None
        """
        """
        super(DoubleGridAlignedMixin, self).set_tile_position(x, y)

        if self.tile_position[0] % 2 == 1 or self.tile_position[1] % 2 == 1:
            cast_position = [math.floor(self.tile_position[0] / 2) * 2,
                             math.floor(self.tile_position[1] / 2) * 2]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported"
                .format(self.tile_position, cast_position),
                RailAlignmentWarning,
                stacklevel = 2
            )