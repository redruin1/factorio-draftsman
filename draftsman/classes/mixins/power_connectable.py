# power_connectable.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities
from draftsman.serialization import draftsman_converters

import attrs


@attrs.define(slots=False)
class PowerConnectableMixin(Exportable):
    """
    Enables the Entity to be connected to power networks.
    """

    @property
    def power_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def maximum_wire_distance(self) -> float:
        """
        The maximum distance that this entity can reach for power connections.
        Returns ``None`` if this entity's name is not recognized by Draftsman.
        Not exported; read only.
        """
        return entities.raw.get(self.name, {"maximum_wire_distance": None})[
            "maximum_wire_distance"
        ]

    # =========================================================================

    _neighbours: list[int] = attrs.field(
        factory=list,
        repr=False,
    )

    @property
    def neighbours(self) -> list:
        """
        The power pole neighbours that this entity connects to.

        ``neighbours`` is traditionally specified as a list of ``ints``, each
        one representing the index of the entity in the parent blueprint that
        this Entity connects to, in 1-indexed notation. For example, if
        ``entity.neighbours == [1, 2]``, then ``entity`` would have power wires
        to ``blueprint.entities[0]`` and ``blueprint.entities[1]``.

        Draftsman implements a more sophisticated neighbours format, where
        entities themselves (or rather, references to them) are used as the
        entries of the ``neighbours`` list. This makes connections independent
        of their location in the parent blueprint, so you can specify power
        connections even before you've placed all the entities in one. Draftsman
        uses this format when making connections, but is still compatible with
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

        :exception DataFormatError: If set to anything that does not match the
            specification above.
        """
        return self._neighbours


draftsman_converters.get_version((1, 0)).add_hook_fns(
    PowerConnectableMixin,
    lambda fields: {"neighbours": fields._neighbours.name},
    lambda fields, converter: {"neighbours": fields._neighbours.name},
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    PowerConnectableMixin,
    lambda fields: {
        "neighbours": fields._neighbours.name,
    },
    lambda fields, converter: {"neighbours": None},
)
