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
from draftsman.signatures import AttrsAsteroidChunkID, uint16
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

    # result_inventory = attrs.field(  # Inventory object, might contain filters later
    #     default=None,
    # )

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=instance_of(Optional[uint16])
    )
    """
    The limiting bar of this Asteroid collector.
    """

    # =========================================================================

    def _chunk_filter_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = AttrsAsteroidChunkID(index=i + 1, name=elem)
                else:
                    res[i] = AttrsAsteroidChunkID.converter(elem)
            return res
        else:
            return value

    chunk_filter: list[AttrsAsteroidChunkID] = attrs.field(
        factory=list,
        converter=_chunk_filter_converter,
        validator=instance_of(list[AttrsAsteroidChunkID]),
    )
    """
    The set of manually specified chunk filters for this asteroid collector.
    Overridden by any circuit filters, if configured and present.
    """

    # TODO: max chunk filters

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

        self.bar = other.bar
        self.chunk_filter = other.chunk_filter
        self.read_contents = other.read_contents
        self.read_hands = other.read_hands

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:asteroid_collector"},
    AsteroidCollector,
    lambda fields: {
        ("result_inventory", "bar"): fields.bar.name,
        "chunk-filter": fields.chunk_filter.name,
        ("control_behavior", "circuit_read_contents"): fields.read_contents.name,
        ("control_behavior", "include_hands"): fields.read_hands.name,
    },
)
