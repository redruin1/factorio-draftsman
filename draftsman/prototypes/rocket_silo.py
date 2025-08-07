# rocket_silo.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.constants import InventoryType, SiloReadMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ModuleID, QualityID, uint32
from draftsman.utils import attrs_reuse, fix_incorrect_pre_init
from draftsman.validators import instance_of, try_convert

from draftsman.data.entities import rocket_silos
from draftsman.data import modules

import attrs
from typing import Iterable, Optional


@fix_incorrect_pre_init
@attrs.define
class RocketSilo(
    ModulesMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that launches rockets, usually to move items between surfaces or
    space platforms.
    """

    @property
    def similar_entities(self) -> list[str]:
        return rocket_silos

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.rocket_silo_modules
            }
        )

    # =========================================================================

    recipe = attrs_reuse(attrs.fields(RecipeMixin).recipe, default="rocket-part")

    # =========================================================================

    auto_launch: Optional[bool] = attrs.field(
        default=False, validator=instance_of(Optional[bool])
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to automatically launch the rocket when it's cargo is
    full.

    .. NOTE::

        Only has an effect on versions of Factorio < 2.0.
    """

    # =========================================================================

    read_items_mode: SiloReadMode = attrs.field(
        default=SiloReadMode.READ_CONTENTS,
        converter=try_convert(SiloReadMode),
        validator=instance_of(SiloReadMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    In which manner this entity should behave when connected to a circuit 
    network.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0.
    """

    # =========================================================================

    use_transitional_requests: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this rocket silo should automatically attempt to fulfill the
    requests of space platforms stationed above it.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0.
    """

    # =========================================================================

    transitional_request_index: uint32 = attrs.field(
        default=0, validator=instance_of(uint32)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    An internal ID used for keeping track of which logistic requests this silo
    should send to space platforms above.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0.
    """

    # =========================================================================

    def request_modules(
        self,
        module_name: ModuleID,
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.rocket_silo_modules, module_name, slots, quality
        )

    # =========================================================================

    def merge(self, other: "RocketSilo"):
        super(RocketSilo, self).merge(other)

        self.auto_launch = other.auto_launch
        self.read_items_mode = other.read_items_mode
        self.transitional_request_index = other.transitional_request_index

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    RocketSilo,
    lambda fields: {
        "auto_launch": fields.auto_launch.name,
        # None: fields.read_items_mode.name,
        # None: fields.use_transitional_requests.name,
        # None: fields.transitional_request_index.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    RocketSilo,
    lambda fields: {
        None: fields.auto_launch.name,
        ("control_behavior", "read_items_mode"): fields.read_items_mode.name,
        "use_transitional_requests": fields.use_transitional_requests.name,
        "transitional_request_index": fields.transitional_request_index.name,
    },
)
