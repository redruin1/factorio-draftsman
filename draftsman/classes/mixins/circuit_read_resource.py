# circuit_read_resource.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import MiningDrillReadMode

from pydantic import BaseModel, Field
from typing import Optional


class CircuitReadResourceMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read the resources underneath it.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_hand.CircuitReadHandMixin`
    """

    class ControlFormat(BaseModel):
        circuit_read_resources: Optional[bool] = Field(
            None,
            description="""
            Whether or not this mining drill should read the amount of resources
            below it.
            """,
        )
        circuit_resource_read_mode: Optional[MiningDrillReadMode] = Field(
            None,
            description="""
            How resources under this mining drill should be broadcast to any 
            connected circuit network, if 'circuit_read_resources' is true.
            """,
        )

    class Format(BaseModel):
        pass

    @property
    def read_resources(self) -> Optional[bool]:
        """
        Whether or not this Entity is set to read the resources underneath to a
        circuit network.

        :getter: Gets the value of ``read_resources``, or ``None`` if not set.
        :setter: Sets the value of ``read_resources``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_resources

    @read_resources.setter
    def read_resources(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_read_resources",
                value,
            )
            self.control_behavior.circuit_read_resources = result
        else:
            self.control_behavior.circuit_read_resources = value

    # =========================================================================

    @property
    def read_mode(self) -> MiningDrillReadMode:
        """
        The mode in which the resources underneath the Entity should be read.
        Either ``MiningDrillReadMode.UNDER_DRILL`` or
        ``MiningDrillReadMode.TOTAL_PATCH``.

        :getter: Gets the value of ``read_mode``, or ``None`` if not set.
        :setter: Sets the value of ``read_mode``.
        :type: :py:data:`~draftsman.constants.MiningDrillReadMode`

        :exception ValueError: If set to anything other than a
            ``MiningDrillReadMode`` value or their ``int`` equivalent.
        """
        return self.control_behavior.circuit_resource_read_mode

    @read_mode.setter
    def read_mode(self, value: MiningDrillReadMode):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_resource_read_mode",
                value,
            )
            self.control_behavior.circuit_resource_read_mode = result
        else:
            self.control_behavior.circuit_resource_read_mode = value
