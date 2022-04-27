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
    Enables the Entity to be connected to power networks.
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
        # type: () -> float
        """
        The maximum distance that this entity can reach for power connections.
        Not exported; read only.

        :type: ``float``
        """
        return self._maximum_wire_distance

    # =========================================================================

    @property
    def neighbours(self):
        # type: () -> list
        """
        The power pole neighbours that this entity connects to.

        ``neighbours`` is traditionally specified as a list of ``ints``, each
        one representing the index of the entity in the parent blueprint that
        this Entity connects to, in 1-indexed notation. For example, if
        ``entity.neighbours == [2, 3]``, then ``entity`` would have power wires
        to ``blueprint.entities[1]`` and ``blueprint.entities[2]``. If you're
        importing from an already existing blueprint string, then this is the
        format you should expect.

        Draftsman implements a more sophisticated neighbours format, where
        entities themselves (or rather, references to them) are used as the
        entries of the ``neighbours`` list. This makes connections independent
        of their location in the parent blueprint, so you can specify power
        connections even before you've placed all the entities in one. Draftsman
        uses this format when making connections, is still compatible with
        simple integers.

        .. WARNING::

            Int-based neighbours lists are fragile; if you want to preserve
            connections in integer format, you have to preserve entity order.
            Any new entities must be added to the end. Keep this in mind when
            importing an already-made blueprint string with connections already
            made.

        .. NOTE::

            Power switch wire connections are abnormal; they are not treated as
            neighbours and instead as special copper circuit connections.
            Inspect an Entity's ``connections`` attribute if you're looking for
            those wires.

        :getter: Gets the neighbours of the Entity.
        :setter: Sets the neighbours of the Entity. Defaults to an empty list if
            set to ``None``.
        :type: See :py:data:`draftsman.signatures.NEIGHBOURS`

        :exception DataFormatError: If set to anything that does not match the
            specification above.
        """
        return self._neighbours

    @neighbours.setter
    def neighbours(self, value):
        # type: (list) -> None
        try:
            self._neighbours = signatures.NEIGHBOURS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
