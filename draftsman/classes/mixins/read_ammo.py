# read_ammo.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class ReadAmmoMixin(Exportable):
    """
    Enables the entity to broadcast its ammo count to the circuit network.
    """

    read_ammo: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to broadcast the amount of ammo currently in this turret to 
    the connected circuit network.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """


draftsman_converters.get_version((2, 0)).add_hook_fns(
    ReadAmmoMixin,
    lambda fields: {("control_behavior", "read_ammo"): fields.read_ammo.name},
)
