# signal.py

from ast import Assert
from factoriotools.signals import (
    SignalID, Signal, signal_IDs, get_signal_type, signal_dict
)
from factoriotools.errors import InvalidSignalID

from unittest import TestCase

class SignalIDTesting(TestCase):
    def test_constructor(self):
        signal_id = SignalID(name = "test-name", type = "example")
        self.assertEqual(signal_id.name, "test-name")
        self.assertEqual(signal_id.type, "example")

    def test_to_dict(self):
        self.assertEqual(
            signal_IDs["signal-0"].to_dict(),
            {"name": "signal-0", "type": "virtual"}
        )

    def test_repr(self):
        self.assertEqual(
            str(signal_IDs["signal-0"]),
            "SignalID{'name': 'signal-0', 'type': 'virtual'}"
        )


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
        try:
            get_signal_type("something invalid")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage

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
        try:
            signal_dict("wrong")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage


class SignalTesting(TestCase):
    def test_constructor(self):
        # String arg
        signal = Signal("transport-belt", 100)
        self.assertEqual(signal.id.name, "transport-belt")
        self.assertEqual(signal.id.type, "item")
        self.assertEqual(signal.count, 100)
        # SignalID arg
        signal = Signal(signal_IDs["transport-belt"], 100)
        self.assertEqual(signal.id.name, "transport-belt")
        self.assertEqual(signal.id.type, "item")
        self.assertEqual(signal.count, 100)
        # Invalid arg
        try:
            signal = Signal(False, 200)
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage

    def test_change_id(self):
        # String arg
        signal = Signal("transport-belt", -25)
        signal.change_id("fast-transport-belt")
        self.assertEqual(signal.id.name, "fast-transport-belt")
        self.assertEqual(signal.count, -25)
        # SignalID arg
        signal.change_id(signal_IDs["express-transport-belt"])
        self.assertEqual(signal.id.name, "express-transport-belt")
        self.assertEqual(signal.count, -25)
        # Invalid arg
        try:
            signal.change_id(False)
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage

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
            "Signal{'count': 100, 'signal': {'name': 'transport-belt', 'type': 'item'}}"
        )