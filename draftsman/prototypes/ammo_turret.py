# ammo_turret.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.constants import Direction
from draftsman.utils import AABB, Rectangle, fix_incorrect_pre_init

from draftsman.data.entities import ammo_turrets

import attrs


# TODO: probably better to make AABB's rotatable into Rectangles rather than
# hardcoding
_vertical_collision = CollisionSet([AABB(-1.41, -1.9, 1.41, 2.1)])
_horizontal_collision = _vertical_collision.rotate(4)
_diagonal_collision = CollisionSet([Rectangle((0, 0), 2.82, 3.0, 45.0)])

_rotated_collision_sets["railgun-turret"] = {
    Direction.NORTH: _vertical_collision,
    Direction.NORTHEAST: _diagonal_collision,
    Direction.EAST: _horizontal_collision,
    Direction.SOUTHEAST: _diagonal_collision.rotate(8),
    Direction.SOUTH: _vertical_collision,
    Direction.SOUTHWEST: _diagonal_collision,
    Direction.WEST: _horizontal_collision,
    Direction.NORTHWEST: _diagonal_collision.rotate(8),
}


@fix_incorrect_pre_init
@attrs.define
class AmmoTurret(
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that automatically targets and attacks other forces within range.
    Consumes item-based ammunition.
    """

    # TODO: validate item_requests match this particular turret type

    @property
    def similar_entities(self) -> list[str]:
        return ammo_turrets

    # =========================================================================

    __hash__ = Entity.__hash__
