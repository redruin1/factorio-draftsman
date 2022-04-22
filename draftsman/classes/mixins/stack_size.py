# stack_size.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six


class StackSizeMixin(object):  # (ControlBehaviorMixin)
    """
    TODO
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(StackSizeMixin, self).__init__(name, similar_entities, **kwargs)

        self.override_stack_size = None
        if "override_stack_size" in kwargs:
            # self.set_stack_size_override(kwargs["override_stack_size"])
            self.override_stack_size = kwargs["override_stack_size"]
            self.unused_args.pop("override_stack_size")
        self._add_export("override_stack_size", lambda x: x is not None)

    # =========================================================================

    @property
    def override_stack_size(self):
        # type: () -> int
        """
        Sets an inserter's stack size override.
        TODO
        """
        return self._override_stack_size

    @override_stack_size.setter
    def override_stack_size(self, value):
        # type: (int) -> None
        if value is None or isinstance(value, six.integer_types):
            self._override_stack_size = value
        else:
            raise TypeError("'value' must be an int or None")

    # =========================================================================

    @property
    def circuit_stack_size_enabled(self):
        # type: () -> bool
        """
        Sets if the inserter's stack size is controlled by circuit signal.
        TODO
        """
        return self.control_behavior.get("circuit_set_stack_size", None)

    @circuit_stack_size_enabled.setter
    def circuit_stack_size_enabled(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_set_stack_size", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_set_stack_size"] = value
        else:
            raise TypeError("'circuit_set_stack_size' must be a bool or None")

    # =========================================================================

    @property
    def stack_control_signal(self):
        # type: () -> dict
        """
        Specify the stack size input signal for the inserter if enabled.
        TODO
        """
        return self.control_behavior.get("stack_control_input_signal", None)

    @stack_control_signal.setter
    def stack_control_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("stack_control_input_signal", None)
            return

        if isinstance(value, six.string_types):
            # Make sure this is a unicode string
            value = six.text_type(value)
            self.control_behavior["stack_control_input_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["stack_control_input_signal"] = value
            except SchemaError as e:
                six.raise_from(DataFormatError(e), None)
