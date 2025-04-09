# logistic_condition.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.signatures import Condition, SignalID, int32

import attrs
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union


@attrs.define(slots=False)
class LogisticConditionMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to have an logistic enable condition, such as when the
    amount of some item in the logistic network exceeds some constant.
    """

    class ControlFormat(BaseModel):
        connect_to_logistic_network: Optional[bool] = Field(
            False,
            description="""
            Whether or not this entity will be controlled from the associated 
            logistic condition.
            """,
        )
        logistic_condition: Optional[Condition] = Field(
            Condition(first_signal=None, comparator="<", constant=0),
            description="""
            The logistic condition that must be passed in order for this entity
            to function, if 'connect_to_logistic_network' is true.
            """,
        )

    class Format(BaseModel):
        pass

    # =========================================================================

    connect_to_logistic_network: bool = attrs.field(
        default=False,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("control_behavior", "connect_to_logistic_network")}
    )

    # @property
    # def connect_to_logistic_network(self) -> bool:
    #     """
    #     Whether or not this entity should use it's logistic network condition to
    #     control its operation (if it has one).

    #     :getter: Gets the value of ``connect_to_logistic_network``, or ``None``
    #         if not set.
    #     :setter: Sets the value of ``connect_to_logistic_network``. Removes the
    #         key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.connect_to_logistic_network

    # @connect_to_logistic_network.setter
    # def connect_to_logistic_network(self, value: bool):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "connect_to_logistic_network",
    #             value,
    #         )
    #         self.control_behavior.connect_to_logistic_network = result
    #     else:
    #         self.control_behavior.connect_to_logistic_network = value

    # =========================================================================

    def set_logistic_condition(
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
        self._set_condition("logistic_condition", a, cmp, b)

    def remove_logistic_condition(self):
        """
        Removes the logistic condition of the Entity. Does nothing if the Entity
        has no logistic condition to remove.
        """
        self.control_behavior.logistic_condition = None
