# test_programmable_speaker.py

from draftsman.entity import ProgrammableSpeaker, programmable_speakers
from draftsman.errors import InvalidEntityID, InvalidSignalID

from schema import SchemaError

from unittest import TestCase

class ProgrammableSpeakerTesting(TestCase):
    def test_default_constructor(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            position = [10, 10],
            parameters = {
                "playback_volume": 1.0,
                "playback_globally": True,
                "allow_polyphony": True
            },
            alert_parameters = {
                "show_alert": True,
                "show_on_map": False,
                "icon_signal_id": "signal-check",
                "alert_message": "some string",
            },
            control_behavior = {
                "circuit_parameters": {
                    "signal_value_is_pitch": False,
                    "instrument_id": 1,
                    "note_id": 1
                }
            }
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 10.5, "y": 10.5},
                "parameters": {
                    "playback_volume": 1.0,
                    "playback_globally": True,
                    "allow_polyphony": True
                },
                "alert_parameters": {
                    "show_alert": True,
                    "show_on_map": False,
                    "icon_signal_id": {
                        "name": "signal-check",
                        "type": "virtual"
                    },
                    "alert_message": "some string"
                },
                "control_behavior": {
                    "circuit_parameters": {
                        "signal_value_is_pitch": False,
                        "instrument_id": 1,
                        "note_id": 1
                    }
                }
            }
        )

        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            position = [10, 10],
            parameters = {
                "playback_volume": 1.0,
                "playback_globally": True,
                "allow_polyphony": True
            },
            alert_parameters = {
                "show_alert": True,
                "show_on_map": False,
                "icon_signal_id": {
                    "name": "signal-check",
                    "type": "virtual"
                },
                "alert_message": "some string",
            },
            control_behavior = {
                "circuit_parameters": {
                    "signal_value_is_pitch": False,
                    "instrument_id": "miscellaneous",
                    "note_id": "alert-destroyed"
                }
            }
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 10.5, "y": 10.5},
                "parameters": {
                    "playback_volume": 1.0,
                    "playback_globally": True,
                    "allow_polyphony": True
                },
                "alert_parameters": {
                    "show_alert": True,
                    "show_on_map": False,
                    "icon_signal_id": {
                        "name": "signal-check",
                        "type": "virtual"
                    },
                    "alert_message": "some string"
                },
                "control_behavior": {
                    "circuit_parameters": {
                        "signal_value_is_pitch": False,
                        "instrument_id": 1,
                        "note_id": 1
                    }
                }
            }
        )

        speaker = ProgrammableSpeaker(
            control_behavior = {
                "circuit_enable_disable": True
            }
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "circuit_enable_disable": True
                }
            }
        )
        speaker = ProgrammableSpeaker(
            control_behavior = {
                "circuit_parameters": {
                    "signal_value_is_pitch": True
                }
            }
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "circuit_parameters": {
                        "signal_value_is_pitch": True
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            ProgrammableSpeaker(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            ProgrammableSpeaker("not a programmable speaker")

    def test_flags(self):
        for name in programmable_speakers:
            speaker = ProgrammableSpeaker(name)
            self.assertEqual(speaker.power_connectable, False)
            self.assertEqual(speaker.dual_power_connectable, False)
            self.assertEqual(speaker.circuit_connectable, True)
            self.assertEqual(speaker.dual_circuit_connectable, False)

    def test_dimensions(self):
        for name in programmable_speakers:
            speaker = ProgrammableSpeaker(name)
            self.assertEqual(speaker.tile_width, 1)
            self.assertEqual(speaker.tile_width, 1)

    def test_set_volume(self):
        speaker = ProgrammableSpeaker()
        speaker.set_volume(0.5)
        self.assertEqual(
            speaker.parameters,
            {
                "playback_volume": 0.5
            }
        )

        speaker.set_volume(None)
        self.assertEqual(speaker.parameters, {})

        # Warnings
        with self.assertWarns(UserWarning):
            speaker.set_volume(10.0)

        self.assertEqual(
            speaker.parameters,
            {
                "playback_volume": 10.0
            }
        )

        # Errors
        with self.assertRaises(SchemaError):
            speaker.set_volume("incorrect")

        self.assertEqual(
            speaker.parameters,
            {
                "playback_volume": 10.0
            }
        )

    def test_set_global_playback(self):
        speaker = ProgrammableSpeaker()
        speaker.set_global_playback(True)
        self.assertEqual(
            speaker.parameters,
            {
                "playback_globally": True
            }
        )
        speaker.set_global_playback(None)
        self.assertEqual(speaker.parameters, {})
        with self.assertRaises(SchemaError):
            speaker.set_global_playback("incorrect")

    def test_set_show_alert(self):
        speaker = ProgrammableSpeaker()
        speaker.set_show_alert(True)
        self.assertEqual(
            speaker.alert_parameters,
            {
                "show_alert": True
            }
        )
        speaker.set_show_alert(None)
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(SchemaError):
            speaker.set_show_alert("incorrect")

    def test_set_polyphony(self):
        speaker = ProgrammableSpeaker()
        speaker.set_polyphony(True)
        self.assertEqual(
            speaker.parameters,
            {
                "allow_polyphony": True
            }
        )
        speaker.set_polyphony(None)
        self.assertEqual(speaker.parameters, {})
        with self.assertRaises(SchemaError):
            speaker.set_polyphony("incorrect")

    def test_set_show_alert_on_map(self):
        speaker = ProgrammableSpeaker()
        speaker.set_show_alert_on_map(True)
        self.assertEqual(
            speaker.alert_parameters,
            {
                "show_on_map": True
            }
        )
        speaker.set_show_alert_on_map(None)
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(SchemaError):
            speaker.set_show_alert_on_map("incorrect")

    def test_set_alert_icon(self):
        speaker = ProgrammableSpeaker()
        speaker.set_alert_icon("signal-check")
        self.assertEqual(
            speaker.alert_parameters,
            {
                "icon_signal_id": {
                    "name": "signal-check",
                    "type": "virtual"
                }
            }
        )
        speaker.set_alert_icon(None)
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(InvalidSignalID):
            speaker.set_alert_icon("incorrect")

    def test_set_alert_message(self):
        speaker = ProgrammableSpeaker()
        speaker.set_alert_message("some string")
        self.assertEqual(
            speaker.alert_parameters,
            {
                "alert_message": "some string"
            }
        )
        speaker.set_alert_message(None)
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(SchemaError):
            speaker.set_alert_message(False)

    def test_set_signal_value_is_pitch(self):
        speaker = ProgrammableSpeaker()
        speaker.set_signal_value_is_pitch(True)
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "signal_value_is_pitch": True
                }
            }
        )
        speaker.set_signal_value_is_pitch(None)
        self.assertEqual(speaker.control_behavior, {})
        speaker.control_behavior = {
            "circuit_parameters": {
                "something": "else",
                "signal_value_is_pitch": False
            }
        }
        speaker.set_signal_value_is_pitch(None)
        self.assertEqual(
            speaker.control_behavior, 
            {
                "circuit_parameters": {
                    "something": "else"
                }
            }
        )
        with self.assertRaises(SchemaError):
            speaker.set_signal_value_is_pitch("incorrect")

    def test_set_instrument(self):
        speaker = ProgrammableSpeaker()
        speaker.set_instrument(0) # integer
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "instrument_id": 0
                }
            }
        )
        speaker.set_instrument("alarms") # string
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "instrument_id": 0
                }
            }
        )
        speaker.set_instrument(None)
        self.assertEqual(speaker.control_behavior, {})
        speaker.set_signal_value_is_pitch(True)
        speaker.set_instrument(None)
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "signal_value_is_pitch": True
                }
            }
        )

        with self.assertRaises(ValueError):
            speaker.set_instrument("incorrect")
        with self.assertRaises(TypeError):
            speaker.set_instrument(TypeError)

    def test_set_note(self):
        speaker = ProgrammableSpeaker()
        speaker.set_note(0) # integer
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "note_id": 0
                }
            }
        )
        speaker.set_note("alarm-1") # string
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "note_id": 0
                }
            }
        )
        speaker.set_note(None)
        self.assertEqual(speaker.control_behavior, {})
        speaker.set_signal_value_is_pitch(True)
        speaker.set_note(None)
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "signal_value_is_pitch": True
                }
            }
        )

        with self.assertRaises(ValueError):
            speaker.set_note("incorrect")
        with self.assertRaises(TypeError):
            speaker.set_note(TypeError)