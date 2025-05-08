# circuit_set_filters.py

from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitSetFiltersMixin:
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to specify its filters from the circuit network.
    """

    # class ControlFormat(BaseModel):
    #     circuit_set_filters: Optional[bool] = Field(
    #         False,
    #         description="""
    #         Whether or not the circuit network sets this entity's filters.
    #         """,
    #     )

    # class Format(BaseModel):
    #     pass

    # =========================================================================

    circuit_set_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should set it's filters via signals given to it
    from connected circuit networks.
    """

    # @property
    # def circuit_set_filters(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.control_behavior.circuit_set_filters

    # @circuit_set_filters.setter
    # def circuit_set_filters(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_set_filters",
    #             value,
    #         )
    #         self.control_behavior.circuit_set_filters = result
    #     else:
    #         self.control_behavior.circuit_set_filters = value


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:circuit_set_filters_mixin"},
    CircuitSetFiltersMixin,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name
    },
)
