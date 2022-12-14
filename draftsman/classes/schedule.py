# schedule.py

from draftsman.classes.association import Association
from draftsman.prototypes.locomotive import Locomotive


class Schedule(object):
    """
    TODO
    """

    def __init__(self):
        self._locomotives = []
        self._stops = []

    # =========================================================================

    @property
    def locomotives(self):
        # type: () -> list[Association]
        """
        TODO
        """
        return self._locomotives

    # =========================================================================

    @property
    def stops(self):
        # type: () -> list[dict]
        """
        TODO
        """
        return self._stops

    def add_locomotive(self, locomotive, stops=None):
        # type: (Locomotive, stops) -> None
        """
        TODO
        """
        if not isinstance(locomotive, Locomotive):
            raise TypeError("'locomotive' must be an instance of <Locomotive>")

        # TODO: handle duplicate locomotives
        self._locomotives.append(Association(locomotive))

    def append_stop(self, name, wait_conditions=None):
        # type: (str, list[dict]) -> None
        """
        TODO
        """
        self.insert_stop(len(self.stops), name, wait_conditions)

    def insert_stop(self, index, name, wait_conditions=[]):
        # type: (int, str, list[dict]) -> None
        """
        TODO
        """
        # TODO: nicer format for `wait_conditions`
        # maybe something like ["full", "or", "time_passed:100s"]
        self._stops.insert(index, {"name": name, "wait_conditions": wait_conditions})

    def to_dict(self):
        # type: () -> dict
        """ """
        return {"locomotives": self._locomotives, "schedule": self._stops}
