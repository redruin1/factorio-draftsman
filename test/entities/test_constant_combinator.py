# test_constant_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ConstantCombinator, constant_combinators
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ConstantCombinatorTesting(TestCase):
    def test_constructor_init(self):
        combinator = ConstantCombinator(
            "constant-combinator",
            tile_position=[0, 2],
            control_behavior={
                "filters": [("signal-A", 100), ("signal-B", 200), ("signal-C", 300)]
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "constant-combinator",
                "position": {"x": 0.5, "y": 2.5},
                "control_behavior": {
                    "filters": [
                        {
                            "index": 1,
                            "signal": {"name": "signal-A", "type": "virtual"},
                            "count": 100,
                        },
                        {
                            "index": 2,
                            "signal": {"name": "signal-B", "type": "virtual"},
                            "count": 200,
                        },
                        {
                            "index": 3,
                            "signal": {"name": "signal-C", "type": "virtual"},
                            "count": 300,
                        },
                    ]
                },
            },
        )

        combinator = ConstantCombinator(
            "constant-combinator",
            tile_position=[0, 2],
            control_behavior={
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {"index": 2, "signal": "signal-B", "count": 200},
                    {
                        "index": 3,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    },
                ]
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "constant-combinator",
                "position": {"x": 0.5, "y": 2.5},
                "control_behavior": {
                    "filters": [
                        {
                            "index": 1,
                            "signal": {"name": "signal-A", "type": "virtual"},
                            "count": 100,
                        },
                        {
                            "index": 2,
                            "signal": {"name": "signal-B", "type": "virtual"},
                            "count": 200,
                        },
                        {
                            "index": 3,
                            "signal": {"name": "signal-C", "type": "virtual"},
                            "count": 300,
                        },
                    ]
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ConstantCombinator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            ConstantCombinator("this is not a constant combinator")

    def test_flags(self):
        for name in constant_combinators:
            combinator = ConstantCombinator(name)
            self.assertEqual(combinator.power_connectable, False)
            self.assertEqual(combinator.dual_power_connectable, False)
            self.assertEqual(combinator.circuit_connectable, True)
            self.assertEqual(combinator.dual_circuit_connectable, False)

    def test_item_slot_count(self):
        combinator = ConstantCombinator()
        self.assertEqual(combinator.item_slot_count, 20)

    def test_set_signal(self):
        combinator = ConstantCombinator()
        combinator.set_signal(0, "signal-A", 100)
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    }
                ]
            },
        )
        combinator.set_signal(1, "signal-B", 200)
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-B", "type": "virtual"},
                        "count": 200,
                    },
                ]
            },
        )
        combinator.set_signal(0, "signal-C", 300)
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-B", "type": "virtual"},
                        "count": 200,
                    },
                ]
            },
        )
        combinator.set_signal(1, None)
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    }
                ]
            },
        )

        with self.assertRaises(TypeError):
            combinator.set_signal(TypeError, "something")
        with self.assertRaises(DataFormatError):
            combinator.set_signal(1, TypeError)
        with self.assertRaises(TypeError):
            combinator.set_signal(1, "iron-ore", TypeError)

    def test_set_signals(self):
        combinator = ConstantCombinator()
        # Test user format
        combinator.set_signals(
            [("signal-A", 100), ("signal-Z", 200), ("iron-ore", 1000)]
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-Z", "type": "virtual"},
                        "count": 200,
                    },
                    {
                        "index": 3,
                        "signal": {"name": "iron-ore", "type": "item"},
                        "count": 1000,
                    },
                ]
            },
        )

        # Test internal format
        combinator.set_signals(
            [
                {
                    "index": 1,
                    "signal": {"name": "signal-A", "type": "virtual"},
                    "count": 100,
                },
                {"index": 2, "signal": "signal-Z", "count": 200},
                {
                    "index": 3,
                    "signal": {"name": "iron-ore", "type": "item"},
                    "count": 1000,
                },
            ]
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-Z", "type": "virtual"},
                        "count": 200,
                    },
                    {
                        "index": 3,
                        "signal": {"name": "iron-ore", "type": "item"},
                        "count": 1000,
                    },
                ]
            },
        )

        # Test clear signals
        combinator.set_signals(None)
        self.assertEqual(combinator.control_behavior, {})

        with self.assertRaises(DataFormatError):
            combinator.set_signals({"something", "wrong"})

    def test_get_signal(self):
        combinator = ConstantCombinator()
        signal = combinator.get_signal(0)
        self.assertEqual(signal, None)
        combinator.set_signals(
            [("signal-A", 100), ("signal-Z", 200), ("iron-ore", 1000)]
        )
        signal = combinator.get_signal(0)
        self.assertEqual(
            signal,
            {
                "index": 1,
                "signal": {"name": "signal-A", "type": "virtual"},
                "count": 100,
            },
        )
        signal = combinator.get_signal(50)
        self.assertEqual(signal, None)
