# read_ammo.py

from draftsman.classes.exportable import attempt_and_reissue

from pydantic import BaseModel, Field
from typing import Optional


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

    @property
    def read_ammo(self) -> bool:
        """
        TODO
        """
        return self.control_behavior.read_ammo

    @read_ammo.setter
    def read_ammo(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_ammo",
                value,
            )
            self.control_behavior.read_ammo = result
        else:
            self.control_behavior.read_ammo = value
