# asteroid_collector.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitSetFiltersMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AsteroidChunkID, Inventory
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import asteroid_collectors

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class AsteroidCollector(
    CircuitSetFiltersMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity which collects asteroid chunks in space.
    """

    @property
    def similar_entities(self) -> list[str]:
        return asteroid_collectors

    # =========================================================================

    result_inventory: Optional[Inventory] = attrs.field(
        factory=Inventory,
        converter=Inventory.converter,
        validator=instance_of(Optional[Inventory]),
    )
    """
    Internal inventory of this asteroid collector. Attempting to set the 
    :py:attr:`~.Inventory.filters` of this object has no effect.
    """

    # =========================================================================

    def _chunk_filter_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = AsteroidChunkID(index=i + 1, name=elem)
                else:
                    res[i] = elem
            return res
        else:
            return value

    chunk_filter: list[AsteroidChunkID] = attrs.field(
        factory=list,
        converter=_chunk_filter_converter,
        validator=instance_of(list[AsteroidChunkID]),
    )
    """
    The set of manually specified chunk filters for this asteroid collector.
    Overridden by any circuit filters, if configured and present.
    """

    # =========================================================================

    read_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this Entity is set to read it's contents to a connected 
    circuit network.

    :exception TypeError: If set to anything other than a ``bool`` or
        ``None``.
    """

    # =========================================================================

    read_hands: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Entity is set to read it's hands to a connected circuit
    network.

    :exception TypeError: If set to anything other than a ``bool`` or
        ``None``.
    """

    # =========================================================================

    def merge(self, other: "AsteroidCollector"):
        super().merge(other)

        self.result_inventory = other.result_inventory
        self.chunk_filter = other.chunk_filter
        self.read_contents = other.read_contents
        self.read_hands = other.read_hands

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    AsteroidCollector,
    lambda fields: {
        "result_inventory": fields.result_inventory.name,
        "chunk-filter": fields.chunk_filter.name,
        ("control_behavior", "circuit_read_contents"): fields.read_contents.name,
        ("control_behavior", "include_hands"): fields.read_hands.name,
    },
)
