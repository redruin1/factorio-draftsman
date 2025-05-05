# circuit_read_resource.py

from draftsman.constants import MiningDrillReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
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

    # =========================================================================

    read_resources: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Entity is set to read the resources underneath to a
    circuit network.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # @property
    # def read_resources(self) -> Optional[bool]:
    #     """
    #     Whether or not this Entity is set to read the resources underneath to a
    #     circuit network.

    #     :getter: Gets the value of ``read_resources``, or ``None`` if not set.
    #     :setter: Sets the value of ``read_resources``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.circuit_read_resources

    # @read_resources.setter
    # def read_resources(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_read_resources",
    #             value,
    #         )
    #         self.control_behavior.circuit_read_resources = result
    #     else:
    #         self.control_behavior.circuit_read_resources = value

    # =========================================================================

    read_mode: MiningDrillReadMode = attrs.field(
        default=MiningDrillReadMode.UNDER_DRILL,
        converter=MiningDrillReadMode,
        validator=instance_of(MiningDrillReadMode),
    )
    """
    The mode in which the resources underneath the Entity should be read.
    Either ``MiningDrillReadMode.UNDER_DRILL`` or
    ``MiningDrillReadMode.TOTAL_PATCH``.

    :exception DataFormatError: If set to anything other than a
        ``MiningDrillReadMode`` value or their ``int`` equivalent.
    """

    # @property
    # def read_mode(self) -> MiningDrillReadMode:
    #     """
    #     The mode in which the resources underneath the Entity should be read.
    #     Either ``MiningDrillReadMode.UNDER_DRILL`` or
    #     ``MiningDrillReadMode.TOTAL_PATCH``.

    #     :getter: Gets the value of ``read_mode``, or ``None`` if not set.
    #     :setter: Sets the value of ``read_mode``.

    #     :exception ValueError: If set to anything other than a
    #         ``MiningDrillReadMode`` value or their ``int`` equivalent.
    #     """
    #     return self.control_behavior.circuit_resource_read_mode

    # @read_mode.setter
    # def read_mode(self, value: MiningDrillReadMode):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_resource_read_mode",
    #             value,
    #         )
    #         self.control_behavior.circuit_resource_read_mode = result
    #     else:
    #         self.control_behavior.circuit_resource_read_mode = value


draftsman_converters.add_schema(
    {"$id": "factorio:circuit_read_resources_mixin"},
    CircuitReadResourceMixin,
    lambda fields: {
        ("control_behavior", "circuit_read_resources"): fields.read_resources.name,
        ("control_behavior", "circuit_resource_read_mode"): fields.read_mode.name,
    },
)
