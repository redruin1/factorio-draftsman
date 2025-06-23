# inserter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import one_of

from draftsman.data.entities import inserters

import attrs
from typing import Literal, Optional


@fix_incorrect_pre_init
@attrs.define
class Inserter(
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity with a swinging arm that can move items between machines.
    """

    @property
    def similar_entities(self) -> list[str]:
        return inserters

    # =========================================================================

    pickup_position: Optional[list[float]] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    The configured pickup position of the inserter. This is *not* the position/
    tile in world space that this inserter would grab an item from; it is 
    instead a position "offset" used for when inserters have custom pickup/
    dropoff locations (think adjustable inserter mods).

    TODO: what do the values mean?

    .. NOTE::

        Only inserters with the ``"allow_custom_vectors"`` key set to ``True`` 
        in their :py:attr:`.prototype` definition will actually allow setting
        these values to have an effect in game.
    """

    # =========================================================================

    drop_position: Optional[list[float]] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    The configured drop position of the inserter. This is *not* the position/
    tile in world space that this inserter would move an item to; it is instead 
    a position "offset" used for when inserters have custom pickup/dropoff 
    locations (think adjustable inserter mods).

    TODO: what do the values mean?

    .. NOTE::

        Only inserters with the ``"allow_custom_vectors"`` key set to ``True`` 
        in their :py:attr:`.prototype` definition will actually allow setting
        these values to have an effect in game.
    """

    # =========================================================================

    filter_mode: Literal["whitelist", "blacklist"] = attrs.field(
        default="whitelist", validator=one_of("whitelist", "blacklist")
    )
    """
    The mode that the given filter should operate under, if the inserter is 
    configured to operate with filters.

    :exception DataFormatError: If set to a value that is neither ``"whitelist"``
        nor ``"blacklist"``.
    """

    # =========================================================================

    spoil_priority: Literal["spoiled-first", "fresh-first", None] = attrs.field(
        default=None,  # TODO: is this true?
        validator=one_of("spoiled-first", "fresh-first", None),
    )
    """
    Whether or not this inserter should prefer most fresh or most spoiled
    items when grabbing from an inventory. If set to ``None``, this inserter
    will ignore the spoiled value of items entirely.

    :raises DataFormatError: When set to a value other than ``"spoiled-first"``,
        ``"fresh-first"``, or ``None``.
    """

    # =========================================================================

    def merge(self, other: "Inserter"):
        super().merge(other)

        self.circuit_set_filters = other.circuit_set_filters
        self.pickup_position = other.pickup_position
        self.drop_position = other.drop_position
        self.filter_mode = other.filter_mode
        self.spoil_priority = other.spoil_priority

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(  # pragma: no branch
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position.name,
        "drop_position": fields.drop_position.name,
        "filter_mode": fields.filter_mode.name,
        None: fields.spoil_priority.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position.name,
        "drop_position": fields.drop_position.name,
        "filter_mode": fields.filter_mode.name,
        "spoil_priority": fields.spoil_priority.name,
    },
)
