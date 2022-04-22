# power_connectable.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.error import DataFormatError

from schema import SchemaError
import six


class PowerConnectableMixin(object):
    """
    TODO
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(PowerConnectableMixin, self).__init__(name, similar_entities, **kwargs)

        self._power_connectable = True

        if "maximum_wire_distance" in entities.raw[self.name]:
            self._maximum_wire_distance = entities.raw[self.name][
                "maximum_wire_distance"
            ]
        else:
            self._maximum_wire_distance = entities.raw[self.name]["wire_max_distance"]

        self.neighbours = []
        if "neighbours" in kwargs:
            self.neighbours = kwargs["neighbours"]
            self.unused_args.pop("neighbours")
        self._add_export("neighbours", lambda x: x is not None and len(x) != 0)

    # =========================================================================

    @property
    def maximum_wire_distance(self):
        # type: () -> int
        """
        Read only
        TODO
        """
        return self._maximum_wire_distance

    # =========================================================================

    @property
    def neighbours(self):
        # type: () -> list
        """
        TODO
        """
        return self._neighbours

    @neighbours.setter
    def neighbours(self, value):
        # type: (list) -> None
        try:
            self._neighbours = signatures.NEIGHBOURS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
