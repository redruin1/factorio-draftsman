# pump.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import pumps

import attrs


@fix_incorrect_pre_init
@attrs.define
class Pump(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that aids fluid transfer through pipes.

    :param name: The name of this entity.
    :param id: A user-given identifier for easy accessing.
    :param quality: The quality of the entity.
    :param position: The position of the entity.
    :param tile_position: The tile position of the entity.
    :param tags: Additional keys, usually populated by mods.
    :param direction: The orientation of the entity.
    :param circuit_condition: The circuit condition that this entity needs to
        satisfy in order to operate.
    :param connect_to_logistic_network: Whether or not this entity should use
        the neighbouring logistic network to influence its behavior.
    :param logistic_condition: The logistic condition that this entity needs to
        satisfy in order to operate.
    :param validate_assignment: Whether or not to validate attribute assignment
        for this entity, either during or after construction.
    :param extra_keys: Any additional dictionary keys/values that are not valid
        under this entity's schema. Unknown keys on import will be collected
        here, and if there are any values
    """

    @property
    def similar_entities(self) -> list[str]:
        return pumps

    # =========================================================================

    __hash__ = Entity.__hash__


Pump.add_schema({"$id": "urn:factorio:entity:pump"})
