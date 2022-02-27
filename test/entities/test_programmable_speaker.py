# test_programmable_speaker.py

from draftsman.entity import ProgrammableSpeaker, programmable_speakers
from draftsman.errors import InvalidEntityID

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

    def test_flags(self):
        pass

    def test_dimensions(self):
        pass

    def test_set_volume(self):
        pass

    def test_set_global_playback(self):
        pass

    def test_set_show_alert(self):
        pass

    def test_set_instrument(self):
        pass

    def test_set_note(self):
        pass