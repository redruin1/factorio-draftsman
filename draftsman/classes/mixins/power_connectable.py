# power_connectable.py

from draftsman.classes.association import Association
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.signatures import uint64

import attrs
from pydantic import BaseModel, Field
from typing import Optional, Union


@attrs.define(slots=False)
class PowerConnectableMixin:
    """
    Enables the Entity to be connected to power networks.
    """

    class Format(BaseModel):
        # 1.0
        # neighbours: Optional[list[Association.Format]] = Field(
        #     [],
        #     description="""
        #     The 'entity_number's of each neighbouring power pole that this power
        #     pole is connected to. Does NOT include power switch copper
        #     connections; see 'connections' key for that.
        #     """,
        # )
        pass

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super(PowerConnectableMixin, self).__init__(name, similar_entities, **kwargs)

    #     # self.neighbours = kwargs.get("neighbours", [])

    # =========================================================================

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

    # @neighbours.setter
    # def neighbours(self, value: list[Union[int, Association]]):
    #     if value is None:
    #         self._root.neighbours = []
    #     else:
    #         self._root.neighbours = value

    # =========================================================================

    # def merge(self, other: Format):
    #     super().merge(other)

    #     # Power Neighbours (union of the two sets, not exceeding 5 connections)
    #     # Iterate over every association in other (the to-be deleted entity)
    #     for association in other.neighbours:
    #         # Keep track of whether or not this association was added to self
    #         association_added = False

    #         # Make sure we don't add the same association multiple times
    #         if association not in self.neighbours:
    #             # Also make sure we don't exceed 5 connections
    #             if len(self.neighbours) < 5:
    #                 self.neighbours.append(association)
    #                 association_added = True

    #         # However, entities that used to point to `other` still do,
    #         # which causes problems since `other` is usually to be deleted
    #         # after merging
    #         # So we now we find the entity that other used to point to and
    #         # iterate over it's neighbours:
    #         associated_entity = association()
    #         for i, old_association in enumerate(associated_entity.neighbours):
    #             # If the association used to point to `other`, make it point
    #             # to `self`
    #             if old_association == Association(other):
    #                 # Only do so, however, if this association is not
    #                 # already in the set of neighbours and we added the
    #                 # connection before, and if we actually even merged the
    #                 # connection in the first place
    #                 if (
    #                     Association(self) not in associated_entity.neighbours
    #                     and association_added
    #                 ):
    #                     associated_entity.neighbours[i] = Association(self)
    #                 else:
    #                     # Otherwise, the association points to an entity
    #                     # that will likely become invalid, so we remove it
    #                     associated_entity.neighbours.remove(old_association)

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.neighbours == other.neighbours


draftsman_converters.get_version((1, 0)).add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:power_connectable_mixin",
    },
    PowerConnectableMixin,
    lambda fields: {"neighbours": fields._neighbours.name},
    lambda fields, converter: {"neighbours": fields._neighbours.name},
)

draftsman_converters.get_version((2, 0)).add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:power_connectable_mixin",
    },
    PowerConnectableMixin,
    lambda fields: {
        "neighbours": fields._neighbours.name,
    },
    lambda fields, converter: {"neighbours": None},
)
