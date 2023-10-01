# circuit_connectable.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.signatures import Connections, recursive_construct
from draftsman.data import entities
from draftsman.error import DataFormatError

from pydantic import BaseModel, ValidationError
import six


class CircuitConnectableMixin(object):
    """
    Enables the Entity to be connected to circuit networks.
    """

    # _exports = {
    #     "connections": {
    #         "format": "TODO",
    #         "description": "All circuit and copper wire connections",
    #         "required": lambda x: len(x) != 0,
    #     }
    # }
    class Format(BaseModel):
        connections: Connections | None = Connections()

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(CircuitConnectableMixin, self).__init__(name, similar_entities, **kwargs)

        self._circuit_connectable = True

        if "circuit_wire_max_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "circuit_wire_max_distance"
            ]
        elif "maximum_wire_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "maximum_wire_distance"
            ]
        elif "wire_max_distance" in entities.raw[self.name]:
            self._circuit_wire_max_distance = entities.raw[self.name][
                "wire_max_distance"
            ]
        else:
            self._circuit_wire_max_distance = None

        self.connections = {}
        if "connections" in kwargs:
            self.connections = kwargs["connections"]
            self.unused_args.pop("connections")
        # self._add_export("connections", lambda x: len(x) != 0)

    # =========================================================================

    @property
    def circuit_wire_max_distance(self):
        # type: () -> int
        """
        The maximum distance that this entity can reach for circuit connections.
        Not exported; read only.

        :type: ``float``
        """
        return self._circuit_wire_max_distance

    # =========================================================================

    @property
    def connections(self):
        # type: () -> dict
        """
        Connections dictionary. Primarily holds information about the Entity's
        circuit connections (as well as copper wire connections).

        :type: See :py:data:`draftsman.signatures.CONNECTIONS`

        :exception DataFormatError: If set to anything that does not match the
            format of :py:data:`draftsman.signatures.CONNECTIONS`.
        """
        return self._root["connections"]

    @connections.setter
    def connections(self, value):
        # type: (dict) -> None
        try:
            # self._root["connections"] = Connections(**value).model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
            self._root["connections"] = recursive_construct(Connections, **value).model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        except ValidationError as e:
            print(e)
            raise DataFormatError from e

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.connections == other.connections
