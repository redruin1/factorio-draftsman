# train_stop.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ColorMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import train_stops
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six
from typing import Union
import warnings


class TrainStop(
    ColorMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
    Entity,
):
    """
    A stop for making train schedules for locomotives.
    """

    def __init__(self, name=train_stops[0], similar_entities=train_stops, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(TrainStop, self).__init__(name, similar_entities, **kwargs)

        self.station = None
        if "station" in kwargs:
            self.station = kwargs["station"]
            self.unused_args.pop("station")
        self._add_export("station", lambda x: x is not None)

        self.manual_trains_limit = None
        if "manual_trains_limit" in kwargs:
            self.manual_trains_limit = kwargs["manual_trains_limit"]
            self.unused_args.pop("manual_trains_limit")
        self._add_export("manual_trains_limit", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def station(self):
        # type: () -> str
        """
        The name of this station.
        """
        return self._station

    @station.setter
    def station(self, value):
        # type: (str) -> None
        if value is None:
            self._station = value
        elif isinstance(value, six.string_types):
            self._station = six.text_type(value)
        else:
            raise TypeError("'station' must be a str or None")

    # =========================================================================

    @property
    def manual_trains_limit(self):
        # type: () -> int
        """
        A limit to the amount of trains that can use this stop. Overridden by
        the circuit signal set train limit (if present).
        """
        return self._manual_trains_limit

    @manual_trains_limit.setter
    def manual_trains_limit(self, value):
        # type: (int) -> None
        if value is None or isinstance(value, int):
            self._manual_trains_limit = value
        else:
            raise TypeError("'manual_trains_limit' must be an int or None")

    # =========================================================================

    @property
    def read_from_train(self):
        # type: () -> bool
        """
        Whether or not to read the train's contents when stopped at this train
        stop.
        """
        return self.control_behavior.get("read_from_train", None)

    @read_from_train.setter
    def read_from_train(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("read_from_train", None)
        elif isinstance(value, bool):
            self.control_behavior["read_from_train"] = value
        else:
            raise TypeError("'read_from_train' must be a bool or None")

    # =========================================================================

    @property
    def read_stopped_train(self):
        # type: () -> bool
        """
        Whether or not to read a unique number associated with the train
        currently stopped at the station.
        """
        return self.control_behavior.get("read_stopped_train", None)

    @read_stopped_train.setter
    def read_stopped_train(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("read_stopped_train", None)
        elif isinstance(value, bool):
            self.control_behavior["read_stopped_train"] = value
        else:
            raise TypeError("'read_stopped_train' must be a bool or None")

    # =========================================================================

    @property
    def train_stopped_signal(self):
        # type: () -> dict
        """
        What signal to output the unique train ID if a train is currently
        stopped at a station.
        """
        return self.control_behavior.get("train_stopped_signal", None)

    @train_stopped_signal.setter
    def train_stopped_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("train_stopped_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["train_stopped_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["train_stopped_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def signal_limits_trains(self):
        # type: () -> bool
        """
        Whether or not an external signal should limit the number of trains that
        can use this stop.
        """
        return self.control_behavior.get("set_trains_limit", None)

    @signal_limits_trains.setter
    def signal_limits_trains(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("set_trains_limit", None)
        elif isinstance(value, bool):
            self.control_behavior["set_trains_limit"] = value
        else:
            raise TypeError("'set_trains_limit' must be a bool or None")

    # =========================================================================

    @property
    def trains_limit_signal(self):
        # type: () -> dict
        """
        What signal to read to limit the number of trains that can use this stop.
        """
        return self.control_behavior.get("trains_limit_signal", None)

    @trains_limit_signal.setter
    def trains_limit_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("trains_limit_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["trains_limit_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["trains_limit_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def read_trains_count(self):
        # type: () -> bool
        """
        Whether or not to read the number of trains that currently use this stop.
        """
        return self.control_behavior.get("read_trains_count", None)

    @read_trains_count.setter
    def read_trains_count(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("read_trains_count", None)
        elif isinstance(value, bool):
            self.control_behavior["read_trains_count"] = value
        else:
            raise TypeError("'read_trains_count' must be a bool or None")

    # =========================================================================

    @property
    def trains_count_signal(self):
        # type: () -> dict
        """
        What signal to use to output the current number of trains that use this
        stop.
        """
        return self.control_behavior.get("trains_count_signal", None)

    @trains_count_signal.setter
    def trains_count_signal(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.control_behavior.pop("trains_count_signal", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.control_behavior["trains_count_signal"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["trains_count_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")
