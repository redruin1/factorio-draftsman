# orientation.py

from draftsman import signatures


class OrientationMixin(object):
    """ 
    Used in trains and wagons to specify their direction. 
    TODO expand
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(OrientationMixin, self).__init__(name, similar_entities, **kwargs)

        self.orientation = 0.0
        if "orientation" in kwargs:
            self.orientation = kwargs["orientation"]
            self.unused_args.pop("orientation")
        self._add_export("orientation", lambda x: x is not None and x != 0)

    # =========================================================================

    @property
    def orientation(self):
        # type: () -> float
        """
        TODO
        """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        # type: (float) -> None
        if value is None or isinstance(value, float):
            self._orientation = value
        else:
            raise TypeError("'orientation' must be a float or None")
        