# accumulator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ControlBehaviorMixin, CircuitConnectableMixin
from draftsman.error import DataFormatError
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import accumulators
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six
import warnings


class Accumulator(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    An entity that stores electricity for periods of high demand.
    """

    def __init__(self, name=accumulators[0], **kwargs):
        # type: (str, **dict) -> None
        super(Accumulator, self).__init__(name, accumulators, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def output_signal(self):
        # type: () -> dict
        """
        The signal used to output this accumulator's charge level, if set.

        :getter: Gets the output signal, or ``None`` if not set.
        :setter: Sets the output signal. Removes the key if set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception InvalidSignalError: If set to a string not recognized as a valid
            signal name.
        :exception DataFormatError: If set to a ``dict`` that does not comply
            with the :py:data:`.SIGNAL_ID` format.
        """
        return self.control_behavior.get("output_signal", None)

    @output_signal.setter
    def output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["output_signal"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)
