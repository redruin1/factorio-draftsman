# read_ammo.py

from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class ReadAmmoMixin:
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the entity to broadcast its ammo count to the circuit network.
    """

    read_ammo: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to broadcast the amount of ammo currently in this turret to 
    the connected circuit network.
    """


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:read_ammo_mixin"},
    ReadAmmoMixin,
    lambda fields: {("control_behavior", "read_ammo"): fields.read_ammo.name},
)
