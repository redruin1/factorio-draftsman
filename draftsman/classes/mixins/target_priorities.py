# target_priorities.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.signatures import Condition, TargetID, SignalID, int32

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Any, Literal, Optional, Union


class TargetPrioritiesMixin:
    """
    Enables the entity to prioritize specific targets either statically or 
    dynamically via the circuit network.
    """
    class ControlFormat(BaseModel):
        set_priority_list: Optional[bool] = Field(
            False,
            description="""
            Whether or not to have the priorities be set by the circuit network.
            If this is True, the contents of "priority-list" are ignored.
            """
        )

        set_ignore_unlisted_targets: Optional[bool] = Field(
            False,
            description="""
            Whether or not target ignoring should be determined by the circuit
            network, determined by "ignore_unlisted_targets_condition".
            """
        )

        ignore_unlisted_targets_condition: Optional[Condition] = Field(
            Condition(),
            description="""
            A condition that enables the entity to ignore enemies not present
            in its targeting filters.
            """
        )

    class Format(BaseModel):
        priority_list: Optional[list[TargetID]] = Field(
            [],
            alias="priority-list",
            description="""
            A list of fixed entities to specify as targets.
            """
        )
        ignore_unprioritized: Optional[bool] = Field(
            False,
            description="""
            Whether or not to completely ignore targets within range if they
            are not present in this entities target filters.
            """
        )

        @field_validator("priority_list", mode="before")
        @classmethod
        def convert_from_str(
            cls, value: Any, info: ValidationInfo
        ):
            try:
                result = []
                for i, elem in enumerate(value):
                    if isinstance(elem, str):
                        result.append({"index": i+1, "name": elem})
                    else:
                        result.append(elem)
                return result
            except:
                return value
            

    # =========================================================================

    @property
    def priority_list(self) -> Optional[list[TargetID]]:
        """
        TODO
        """
        return self._root.priority_list

    @priority_list.setter
    def priority_list(self, value: Optional[list[TargetID]]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "priority_list",
                value,
            )
            self._root.priority_list = result
        else:
            self._root.priority_list = value

    # =========================================================================

    @property
    def ignore_unprioritized(self) -> Optional[bool]:
        """
        TODO
        """
        return self._root.ignore_unprioritized

    @ignore_unprioritized.setter
    def ignore_unprioritized(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "ignore_unprioritized",
                value,
            )
            self._root.ignore_unprioritized = result
        else:
            self._root.ignore_unprioritized = value

    # =========================================================================

    @property
    def set_priority_list(self) -> Optional[bool]:
        """
        TODO
        """
        return self.control_behavior.set_priority_list
    
    @set_priority_list.setter
    def set_priority_list(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "set_priority_list",
                value,
            )
            self.control_behavior.set_priority_list = result
        else:
            self.control_behavior.set_priority_list = value

    # =========================================================================

    @property
    def set_ignore_unlisted_targets(self) -> Optional[bool]:
        """
        TODO
        """
        return self.control_behavior.set_ignore_unlisted_targets
    
    @set_ignore_unlisted_targets.setter
    def set_ignore_unlisted_targets(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "set_ignore_unlisted_targets",
                value,
            )
            self.control_behavior.set_ignore_unlisted_targets = result
        else:
            self.control_behavior.set_ignore_unlisted_targets = value

    # =========================================================================

    def set_ignore_unlisted_targets_condition(
        self,
        a: Union[SignalID, None] = None,
        cmp: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "<",
        b: Union[SignalID, int32] = 0,
    ):
        """
        Sets the logistic condition of the Entity.

        ``cmp`` can be specified as stored as the single unicode character which
        is used by Factorio, or you can use the Python formatted 2-character
        equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they are converted to and stored as
        the first format.

        :param a: The string name of the first signal.
        :param cmp: The operation to use, as specified above.
        :param b: The string name of the second signal, or some 32-bit constant.

        :exception DataFormatError: If ``a`` is not a valid signal name, if
            ``cmp`` is not a valid operation, or if ``b`` is neither a valid
            signal name nor a constant.
        """
        self._set_condition("ignore_unlisted_targets_condition", a, cmp, b)

    def remove_ignore_unlisted_targets_condition(self):
        """
        Removes the logistic condition of the Entity. Does nothing if the Entity
        has no logistic condition to remove.
        """
        self.control_behavior.ignore_unlisted_targets_condition = None
