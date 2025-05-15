# rocket_silo.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
)
from draftsman.constants import SiloReadMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import RecipeName, uint32
from draftsman.validators import instance_of, try_convert

from draftsman.data.entities import rocket_silos

import attrs
from typing import Optional


@attrs.define
class RocketSilo(
    ModulesMixin,
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
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

    # TODO: we should just "evolve" the attribute instead of redefining it
    # See https://github.com/python-attrs/attrs/issues/637
    recipe: Optional[RecipeName] = attrs.field(
        default="rocket-part", validator=instance_of(Optional[RecipeName])
    )

    # =========================================================================

    auto_launch: Optional[bool] = attrs.field(
        default=False, validator=instance_of(Optional[bool])
    )
    """
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
    In which manner this entity should behave when connected to a circuit 
    network.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0.
    """

    # =========================================================================

    transitional_request_index: uint32 = attrs.field(
        default=0, validator=instance_of(uint32)
    )
    """
    An internal ID used for keeping track of which logistic requests this silo
    should send to space platforms above.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0.
    """

    # =========================================================================

    def merge(self, other: "RocketSilo"):
        super(RocketSilo, self).merge(other)

        self.auto_launch = other.auto_launch
        self.read_items_mode = other.read_items_mode
        self.transitional_request_index = other.transitional_request_index

    # =========================================================================

    __hash__ = Entity.__hash__


RocketSilo.add_schema(
    {
        "$id": "urn:factorio:entity:rocket-silo",
        "properties": {"auto_launch": {"type": "boolean", "default": "false"}},
    },
    version=(1, 0),
    mro=(ItemRequestMixin, RecipeMixin, Entity),
)

draftsman_converters.get_version((1, 0)).add_hook_fns(  # pragma: no branch
    RocketSilo,
    lambda fields: {
        "auto_launch": fields.auto_launch.name,
        None: fields.read_items_mode.name,
        None: fields.transitional_request_index.name,
    },
)

RocketSilo.add_schema(
    {
        "$id": "urn:factorio:entity:rocket-silo",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "read_items_mode": {
                        "enum": [
                            SiloReadMode.NONE,
                            SiloReadMode.READ_CONTENTS,
                            SiloReadMode.READ_ORBITAL_REQUESTS,
                        ],
                        "default": SiloReadMode.READ_CONTENTS,
                    }
                },
            },
            "transitional_request_index": {"$ref": "urn:uint32"},
        },
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    RocketSilo,
    lambda fields: {
        None: fields.auto_launch.name,
        ("control_behavior", "read_items_mode"): fields.read_items_mode.name,
        "transitional_request_index": fields.transitional_request_index.name,
    },
)
