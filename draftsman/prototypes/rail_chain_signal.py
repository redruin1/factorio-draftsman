# rail_chain_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
)
from draftsman import signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rail_chain_signals
from draftsman.data.signals import signal_dict
from draftsman.data import entities

from schema import SchemaError
import six
from typing import Union
import warnings


class RailChainSignal(
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
    Entity,
):
    """
    A rail signal that allows determines access of a current rail block based on
    a forward rail block.
    """

    def __init__(self, name=rail_chain_signals[0], **kwargs):
        # type: (str, **dict) -> None
        super(RailChainSignal, self).__init__(name, rail_chain_signals, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {"floor-layer", "rail-layer", "item-layer"}

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def blue_output_signal(self):
        # type: () -> dict
        """
        The blue output signal. Sent when the rail signal's state is blue.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the blue output signal, or ``None`` if not set.
        :setter: Sets the blue output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
        """
        return self.control_behavior.get("blue_output_signal", None)

    @blue_output_signal.setter
    def blue_output_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("blue_output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["blue_output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["blue_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    # def on_insert(self, parent):
    #     # Check if the rail_signal is adjacent to a rail
    #     # This test has to be more sophisticated than just testing for adjacent
    #     # entities; we also must consider the orientation of signal to ensure
    #     # it is facing the correct direction (must be on the right side of the
    #     # track, unless there exists another signal on the opposite side)
    #     pass
