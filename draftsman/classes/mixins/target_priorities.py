# target_priorities.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman import signatures
from draftsman.validators import instance_of

import attrs
from typing import Union


@attrs.define(slots=False)
class TargetPrioritiesMixin(Exportable):
    """
    Enables the entity to prioritize specific targets either statically or
    dynamically via the circuit network.
    """

    def _priority_list_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    res[i] = signatures.TargetID(index=i, name=elem)
                else:
                    res[i] = elem
            return res
        return value

    priority_list: list[signatures.TargetID] = attrs.field(
        factory=list,
        converter=_priority_list_converter,
        validator=instance_of(list[signatures.TargetID]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    A (static) list of entities to prefer targeting. Overwritten by values given
    by the circuit network if :py:attr:`set_priority_list` is ``True``.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    ignore_unprioritized: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to entirely ignore enemies not present in it's 
    :py:attr:`.priority_list`. This value is overridden by the circuit network
    if :py:attr:`.set_ignore_prioritized` is ``True``.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    set_priority_list: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not priority filters should be set via the circuit network.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    set_ignore_unprioritized: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    If this value is ``True``, the turret will only ignore unprioritized targets
    if the condition :py:attr:`.ignore_unlisted_targets_condition` passes.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    ignore_unlisted_targets_condition: signatures.Condition = attrs.field(
        factory=signatures.Condition,
        converter=signatures.Condition.converter,
        validator=instance_of(signatures.Condition),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The condition to use when determining whether or not to ignore unprioritized
    targets dynamically via the circuit network.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    def set_ignore_unlisted_targets_condition(
        self,
        first_operand: Union[signatures.SignalID, None] = None,
        comparator: signatures.Comparator = "<",
        second_operand: Union[signatures.SignalID, signatures.int32] = 0,
    ):
        """
        Sets the condition under which non-prioritized targets should be ignored.

        ``comparator`` can be specified as stored as the single unicode character which
        is used by Factorio, or you can use the Python formatted 2-character
        equivalents::

            # One of:
            [">", "<", "=",  "≥",  "≤",  "≠"]
            # Or, alternatively:
            [">", "<", "==", ">=", "<=", "!="]

        If specified in the second format, they are converted to and stored as
        the first format.

        :param first_operand: The string name of the first signal.
        :param comparator: The operation to use, as specified above.
        :param second_operand: The string name of the second signal, or some
            32-bit constant.

        :exception DataFormatError: If ``first_operand`` is not a valid signal
            name, if ``comparator`` is not a valid operation, or if
            ``second_operand`` is neither a valid signal name nor a constant.
        """
        self._set_condition(
            "ignore_unlisted_targets_condition",
            first_operand,
            comparator,
            second_operand,
        )


draftsman_converters.get_version((2, 0)).add_hook_fns(
    TargetPrioritiesMixin,
    lambda fields: {
        "priority_list": fields.priority_list.name,
        "ignore_unprioritized": fields.ignore_unprioritized.name,
        "set_priority_list": fields.set_priority_list.name,
        "set_ignore_unprioritized": fields.set_ignore_unprioritized.name,
        "ignore_unlisted_targets_condition": fields.ignore_unlisted_targets_condition.name,
    },
)
