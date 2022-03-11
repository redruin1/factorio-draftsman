# signal.py

from draftsman.signal import Signal
from draftsman.error import InvalidSignalError
from draftsman.utils import get_signal_type, signal_dict

import draftsman.data.signals as signals

from unittest import TestCase


class SignalUtilsTesting(TestCase):
    pairs = {
        "transport-belt": "item",
        "offshore-pump": "item",
        "signal-anything": "virtual",
        "signal-red": "virtual",
        "crude-oil": "fluid",
        "steam": "fluid"
    }

    def test_get_signal_type(self):
        # Valid pairs
        for signal_name, signal_type in self.pairs.items():
            self.assertEqual(
                get_signal_type(signal_name),
                signal_type
            )
        # Invalid name
        with self.assertRaises(InvalidSignalError):
            get_signal_type("something invalid")

    def test_signal_dict(self):
        # Valid pairs
        for signal_name, signal_type in self.pairs.items():
            self.assertEqual(
                signal_dict(signal_name),
                {
                    "name": signal_name,
                    "type": signal_type
                }
            )
        # Invalid name
        with self.assertRaises(InvalidSignalError):
            signal_dict("wrong")


class SignalTesting(TestCase):
    def test_constructor(self):
        # String arg
        signal = Signal("transport-belt", 100)
        self.assertEqual(signal.name, "transport-belt")
        self.assertEqual(signal.type, "item")
        self.assertEqual(signal.count, 100)
        # Invalid arg
        with self.assertRaises(InvalidSignalError):
            signal = Signal(False, 200)

    def test_change_id(self):
        # String arg
        signal = Signal("transport-belt", -25)
        signal.set_name("fast-transport-belt")
        self.assertEqual(signal.name, "fast-transport-belt")
        self.assertEqual(signal.type, "item")
        self.assertEqual(signal.count, -25)
        # Invalid arg
        with self.assertRaises(InvalidSignalError):
            signal.set_name(False)

    def test_to_dict(self):
        signal = Signal("transport-belt", 2000000000)
        self.assertEqual(
            signal.to_dict(),
            {
                "signal": {
                    "name": "transport-belt",
                    "type": "item"
                },
                "count": 2000000000
            }
        )
        signal.count = 100
        self.assertEqual(
            signal.to_dict(),
            {
                "signal": {
                    "name": "transport-belt",
                    "type": "item"
                },
                "count": 100
            }
        )

    def test_repr(self):
        signal = Signal("transport-belt", 100)
        self.assertEqual(
            str(signal),
            "Signal{'signal': {'name': 'transport-belt', 'type': 'item'}, 'count': 100}"
        )