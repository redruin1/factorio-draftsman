# test_rail_chain_signal.py

from draftsman.entity import RailChainSignal, rail_chain_signals
from draftsman.errors import InvalidEntityID, InvalidSignalID

from schema import SchemaError

from unittest import TestCase

class RailChainSignalTesting(TestCase):
    def test_default_constructor(self):
        rail_signal = RailChainSignal()
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5}
            }
        )
    
    def test_constructor_init(self):
        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior = {}
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
            }
        )

        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior = {
                "red_output_signal": "signal-A",
                "yellow_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D"
            }
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "yellow_output_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "green_output_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                    "blue_output_signal": {
                        "name": "signal-D",
                        "type": "virtual"
                    },
                }
            }
        )
        
        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior = {
                "red_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                },
                "yellow_output_signal": {
                    "name": "signal-B",
                    "type": "virtual"
                },
                "green_output_signal": {
                    "name": "signal-C",
                    "type": "virtual"
                },
                "blue_output_signal": {
                    "name": "signal-D",
                    "type": "virtual"
                }
            }
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "yellow_output_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "green_output_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                    "blue_output_signal": {
                    "name": "signal-D",
                    "type": "virtual"
                    }
                }
            }
        )

        # Warnings:
        with self.assertWarns(UserWarning):
            RailChainSignal("rail-chain-signal", invalid_keyword = "whatever")
        # Warn if the rail signal is not placed next to rail
        # TODO (Complex)

        # Errors:
        with self.assertRaises(InvalidEntityID):
            RailChainSignal("this is not a rail chain signal")

    def test_dimensions(self):
        for name in rail_chain_signals:
            rail_signal = RailChainSignal(name)
            self.assertEqual(rail_signal.tile_width, 1)
            self.assertEqual(rail_signal.tile_height, 1)

    def test_set_blue_output_signal(self):
        rail_signal = RailChainSignal()
        rail_signal.set_blue_output_signal("signal-A")
        self.assertEqual(
            rail_signal.control_behavior,
            {
                "blue_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        rail_signal.set_blue_output_signal(None)
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            rail_signal.set_blue_output_signal("incorrect")