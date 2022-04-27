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
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to set red, yellow, and green circuit output signals.
    """

    @property
    def red_output_signal(self):
        # type: () -> dict
        """
        The red output signal. Sent when the rail signal's state is red.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the red output signal, or ``None`` if not set.
        :setter: Sets the red output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
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
        The yellow output signal. Sent when the rail signal's state is yellow.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the yellow output signal, or ``None`` if not set.
        :setter: Sets the yellow output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
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
        The green output signal. Sent when the rail signal's state is green.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the green output signal, or ``None`` if not set.
        :setter: Sets the green output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
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
