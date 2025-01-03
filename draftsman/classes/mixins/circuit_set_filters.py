# circuit_set_filters.py

from draftsman.classes.exportable import attempt_and_reissue

from pydantic import BaseModel, Field
from typing import Optional


class CircuitSetFiltersMixin:
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to specify its filters from the circuit network.
    """

    class ControlFormat(BaseModel):
        circuit_set_filters: Optional[bool] = Field(
            False,
            description="""
            Whether or not the circuit network sets this entity's filters.
            """,
        )

    class Format(BaseModel):
        pass

    # =========================================================================

    @property
    def circuit_set_filters(self) -> Optional[bool]:
        """
        TODO
        """
        return self.control_behavior.circuit_set_filters

    @circuit_set_filters.setter
    def circuit_set_filters(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_set_filters",
                value,
            )
            self.control_behavior.circuit_set_filters = result
        else:
            self.control_behavior.circuit_set_filters = value
