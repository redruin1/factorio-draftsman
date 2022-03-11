# train_stop.py

from draftsman.prototypes.mixins import (
    ColorMixin, CircuitConditionMixin, EnableDisableMixin, 
    LogisticConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    DoubleGridAlignedMixin, DirectionalMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import train_stops

import warnings


class TrainStop(ColorMixin, CircuitConditionMixin, EnableDisableMixin, 
                LogisticConditionMixin, ControlBehaviorMixin, 
                CircuitConnectableMixin, DoubleGridAlignedMixin, 
                DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = train_stops[0], **kwargs):
        # type: (str, **dict) -> None
        super(TrainStop, self).__init__(name, train_stops, **kwargs)

        self.station = None
        if "station" in kwargs:
            self.set_station_name(kwargs["station"])
            self.unused_args.pop("station")
        self._add_export("station", lambda x: x is not None)

        self.manual_trains_limit = None
        if "manual_trains_limit" in kwargs:
            self.set_manual_trains_limit(kwargs["manual_trains_limit"])
            self.unused_args.pop("manual_trains_limit")
        self._add_export("manual_trains_limit", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_station_name(self, name):
        # type: (str) -> None
        """
        """
        self.station = signatures.STRING.validate(name)

    def set_manual_trains_limit(self, amount):
        # type: (int) -> None
        """
        """
        self.manual_trains_limit = signatures.INTEGER.validate(amount)

    def set_read_from_train(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("read_from_train", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["read_from_train"] = value

    def set_read_stopped_train(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("read_stopped_train", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["read_stopped_train"] = value
        
        # This bit might be desirable, might not be
        # if value is True and \
        #    "train_stopped_signal" not in self.control_behavior:
        #     # Set default signal
        #     self.control_behavior["train_stopped_signal"] = signal_dict("signal-T")

    def set_train_stopped_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("train_stopped_signal", None)
        else:
            self.control_behavior["train_stopped_signal"] = signal_dict(signal)

        # This bit might be desirable, might not be
        # if signal is not None and \
        #    "read_stopped_train" not in self.control_behavior:
        #     # Enable train signal reading
        #     self.control_behavior["read_stopped_train"] = True

    def set_trains_limit(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("set_trains_limit", None)
        else:
            value =  signatures.BOOLEAN.validate(value)
            self.control_behavior["set_trains_limit"] = value

    def set_trains_limit_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("trains_limit_signal", None)
        else:
            self.control_behavior["trains_limit_signal"] = signal_dict(signal)

    def set_read_trains_count(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("read_trains_count", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["read_trains_count"] = value

    def set_trains_count_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("trains_count_signal", None)
        else:
            self.control_behavior["trains_count_signal"] = signal_dict(signal)