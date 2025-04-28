# read_ammo.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
class ReadAmmoMixin:
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the entity to broadcast its ammo count to the circuit network.
    """

    class ControlFormat(BaseModel):
        read_ammo: Optional[bool] = Field(
            True,
            description="""
            Whether or not to broadcast the ammo count to connected circuit
            networks.
            """,
        )

    class Format(BaseModel):
        pass

    # =========================================================================

    read_ammo: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    TODO
    """

    # @property
    # def read_ammo(self) -> bool:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.read_ammo

    # @read_ammo.setter
    # def read_ammo(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_ammo",
    #             value,
    #         )
    #         self.control_behavior.read_ammo = result
    #     else:
    #         self.control_behavior.read_ammo = value


draftsman_converters.add_schema(
    {"$id": "factorio:read_ammo_mixin"},
    ReadAmmoMixin,
    lambda fields: {fields.read_ammo.name: ("control_behavior", "read_ammo")},
)
