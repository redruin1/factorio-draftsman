# roboport.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ControlBehaviorMixin, CircuitConnectableMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import roboports
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six
from typing import Union
import warnings


class Roboport(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    An entity that acts as a node in a logistics network.
    """

    def __init__(self, name=roboports[0], **kwargs):
        # type: (str, **dict) -> None
        super(Roboport, self).__init__(name, roboports, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def read_logistics(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("read_logistics", None)

    @read_logistics.setter
    def read_logistics(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("read_logistics", None)
        elif isinstance(value, bool):
            self.control_behavior["read_logistics"] = value
        else:
            raise TypeError("'read_logistics' must be a bool or None")

    # =========================================================================

    @property
    def read_robot_stats(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("read_robot_stats", None)

    @read_robot_stats.setter
    def read_robot_stats(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("read_robot_stats", None)
        elif isinstance(value, bool):
            self.control_behavior["read_robot_stats"] = value
        else:
            raise TypeError("'read_robot_stats' must be a bool or None")

    # =========================================================================

    @property
    def available_logistic_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("available_logistic_output_signal", None)

    @available_logistic_signal.setter
    def available_logistic_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("available_logistic_output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["available_logistic_output_signal"] = signal_dict(
                value
            )
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["available_logistic_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def total_logistic_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("total_logistic_output_signal", None)

    @total_logistic_signal.setter
    def total_logistic_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("total_logistic_output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["total_logistic_output_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["total_logistic_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def available_construction_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("available_construction_output_signal", None)

    @available_construction_signal.setter
    def available_construction_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("available_construction_output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["available_construction_output_signal"] = signal_dict(
                value
            )
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["available_construction_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def total_construction_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("total_construction_output_signal", None)

    @total_construction_signal.setter
    def total_construction_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("total_construction_output_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["total_construction_output_signal"] = signal_dict(
                value
            )
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["total_construction_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")
