# double_grid_aligned.py


class DoubleGridAlignedMixin:
    """
    Makes the Entity issue warnings if set to an odd tile-position coordinate.
    Sets the ``double_grid_aligned`` attribute to ``True``.
    """

    @property
    def double_grid_aligned(self) -> bool:
        return True
