# signal.py

from draftsman.signal import Signal
from draftsman.error import InvalidSignalError
from draftsman.utils import get_signal_type, signal_dict

import draftsman.data.signals as signals

from unittest import TestCase


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

    def test_set_count(self):
        signal = Signal("transport-belt", -25)
        signal.set_count(100000)
        self.assertEqual(signal.count, 100000)
        with self.assertRaises(ValueError):
            signal.set_count("incorrect")

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