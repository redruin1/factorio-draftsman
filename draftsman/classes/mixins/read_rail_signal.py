# read_rail_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six


class ReadRailSignalMixin(object):  # (ControlBehaviorMixin)
    """
    TODO
    """

    @property
    def red_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("red_output_signal", None)

    @red_output_signal.setter
    def red_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("red_output_signal", None)
        elif isinstance(value, six.string_types):
            # Make sure this is a unicode string
            value = six.text_type(value)
            self.control_behavior["red_output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["red_output_signal"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def yellow_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("yellow_output_signal", None)

    @yellow_output_signal.setter
    def yellow_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("yellow_output_signal", None)
        elif isinstance(value, six.string_types):
            # Make sure this is a unicode string
            value = six.text_type(value)
            self.control_behavior["yellow_output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["yellow_output_signal"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def green_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior["green_output_signal"]

    @green_output_signal.setter
    def green_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("green_output_signal", None)
        elif isinstance(value, six.string_types):
            # Make sure this is a unicode string
            value = six.text_type(value)
            self.control_behavior["green_output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["green_output_signal"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)
