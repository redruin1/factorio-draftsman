# test_programmable_speaker.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ProgrammableSpeaker, programmable_speakers
from draftsman.error import (
    DraftsmanError,
    InvalidEntityError,
    InvalidSignalError,
    InvalidInstrumentID,
    InvalidNoteID,
)
from draftsman.warning import DraftsmanWarning, VolumeRangeWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ProgrammableSpeakerTesting(TestCase):
    def test_constructor_init(self):
        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            tile_position=[10, 10],
            parameters={
                "playback_volume": 1.0,
                "playback_globally": True,
                "allow_polyphony": True,
            },
            alert_parameters={
                "show_alert": True,
                "show_on_map": False,
                "icon_signal_id": "signal-check",
                "alert_message": "some string",
            },
            control_behavior={
                "circuit_parameters": {
                    "signal_value_is_pitch": False,
                    "instrument_id": 1,
                    "note_id": 1,
                }
            },
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 10.5, "y": 10.5},
                "parameters": {
                    "playback_volume": 1.0,
                    "playback_globally": True,
                    "allow_polyphony": True,
                },
                "alert_parameters": {
                    "show_alert": True,
                    "show_on_map": False,
                    "icon_signal_id": {"name": "signal-check", "type": "virtual"},
                    "alert_message": "some string",
                },
                "control_behavior": {
                    "circuit_parameters": {
                        "signal_value_is_pitch": False,
                        "instrument_id": 1,
                        "note_id": 1,
                    }
                },
            },
        )

        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            tile_position=[10, 10],
            parameters={
                "playback_volume": 1.0,
                "playback_globally": True,
                "allow_polyphony": True,
            },
            alert_parameters={
                "show_alert": True,
                "show_on_map": False,
                "icon_signal_id": {"name": "signal-check", "type": "virtual"},
                "alert_message": "some string",
            },
            control_behavior={
                "circuit_parameters": {
                    "signal_value_is_pitch": False,
                    "instrument_id": 1,
                    "note_id": 1,
                }
            },
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 10.5, "y": 10.5},
                "parameters": {
                    "playback_volume": 1.0,
                    "playback_globally": True,
                    "allow_polyphony": True,
                },
                "alert_parameters": {
                    "show_alert": True,
                    "show_on_map": False,
                    "icon_signal_id": {"name": "signal-check", "type": "virtual"},
                    "alert_message": "some string",
                },
                "control_behavior": {
                    "circuit_parameters": {
                        "signal_value_is_pitch": False,
                        "instrument_id": 1,
                        "note_id": 1,
                    }
                },
            },
        )

        speaker = ProgrammableSpeaker(control_behavior={"circuit_enable_disable": True})
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"circuit_enable_disable": True},
            },
        )
        speaker = ProgrammableSpeaker(
            control_behavior={"circuit_parameters": {"signal_value_is_pitch": True}}
        )
        self.assertEqual(
            speaker.to_dict(),
            {
                "name": "programmable-speaker",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "circuit_parameters": {"signal_value_is_pitch": True}
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ProgrammableSpeaker(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            ProgrammableSpeaker("not a programmable speaker")

    def test_flags(self):
        for name in programmable_speakers:
            speaker = ProgrammableSpeaker(name)
            self.assertEqual(speaker.power_connectable, False)
            self.assertEqual(speaker.dual_power_connectable, False)
            self.assertEqual(speaker.circuit_connectable, True)
            self.assertEqual(speaker.dual_circuit_connectable, False)

    def test_get_instruments(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(
            speaker.instruments["alarms"],
            {"alarm-1", "alarm-2", "buzzer-1", "buzzer-2", "buzzer-3", "ring", "siren"},
        )

    def test_set_parameters(self):
        speaker = ProgrammableSpeaker()
        speaker.parameters = None
        self.assertEqual(speaker.parameters, {})

        with self.assertRaises(TypeError):
            speaker.parameters = "false"

    def test_set_alert_parameters(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_parameters = None
        self.assertEqual(speaker.alert_parameters, {})

        with self.assertRaises(TypeError):
            speaker.alert_parameters = "false"

    def test_set_volume(self):
        speaker = ProgrammableSpeaker()
        speaker.volume = 0.5
        self.assertEqual(speaker.volume, 0.5)
        self.assertEqual(speaker.parameters, {"playback_volume": 0.5})
        speaker.volume = None
        self.assertEqual(speaker.parameters, {})

        # Warnings
        with self.assertWarns(VolumeRangeWarning):
            speaker.volume = 10.0

        self.assertEqual(speaker.parameters, {"playback_volume": 10.0})

        # Errors
        with self.assertRaises(TypeError):
            speaker.volume = "incorrect"

        self.assertEqual(speaker.parameters, {"playback_volume": 10.0})

    def test_set_global_playback(self):
        speaker = ProgrammableSpeaker()
        speaker.global_playback = True
        self.assertEqual(speaker.global_playback, True)
        self.assertEqual(speaker.parameters, {"playback_globally": True})
        speaker.global_playback = None
        self.assertEqual(speaker.parameters, {})
        with self.assertRaises(TypeError):
            speaker.global_playback = "incorrect"

    def test_set_show_alert(self):
        speaker = ProgrammableSpeaker()
        speaker.show_alert = True
        self.assertEqual(speaker.show_alert, True)
        self.assertEqual(speaker.alert_parameters, {"show_alert": True})
        speaker.show_alert = None
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(TypeError):
            speaker.show_alert = "incorrect"

    def test_set_polyphony(self):
        speaker = ProgrammableSpeaker()
        speaker.allow_polyphony = True
        self.assertEqual(speaker.allow_polyphony, True)
        self.assertEqual(speaker.parameters, {"allow_polyphony": True})
        speaker.allow_polyphony = None
        self.assertEqual(speaker.parameters, {})
        with self.assertRaises(TypeError):
            speaker.allow_polyphony = "incorrect"

    def test_set_show_alert_on_map(self):
        speaker = ProgrammableSpeaker()
        speaker.show_alert_on_map = True
        self.assertEqual(speaker.show_alert_on_map, True)
        self.assertEqual(speaker.alert_parameters, {"show_on_map": True})
        speaker.show_alert_on_map = None
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(TypeError):
            speaker.show_alert_on_map = "incorrect"

    def test_set_alert_icon(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_icon = "signal-check"
        self.assertEqual(
            speaker.alert_icon, {"name": "signal-check", "type": "virtual"}
        )
        self.assertEqual(
            speaker.alert_parameters,
            {"icon_signal_id": {"name": "signal-check", "type": "virtual"}},
        )
        speaker.alert_icon = {"name": "signal-check", "type": "virtual"}
        self.assertEqual(
            speaker.alert_parameters,
            {"icon_signal_id": {"name": "signal-check", "type": "virtual"}},
        )
        speaker.alert_icon = None
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(TypeError):
            speaker.alert_icon = TypeError
        with self.assertRaises(InvalidSignalError):
            speaker.alert_icon = "incorrect"

    def test_set_alert_message(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_message = "some string"
        self.assertEqual(speaker.alert_message, "some string")
        self.assertEqual(speaker.alert_parameters, {"alert_message": "some string"})
        speaker.alert_message = None
        self.assertEqual(speaker.alert_parameters, {})
        with self.assertRaises(TypeError):
            speaker.alert_message = False

    def test_set_signal_value_is_pitch(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(speaker.signal_value_is_pitch, None)
        speaker.signal_value_is_pitch = True
        self.assertEqual(speaker.signal_value_is_pitch, True)
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"signal_value_is_pitch": True}},
        )
        speaker.signal_value_is_pitch = None
        self.assertEqual(speaker.control_behavior, {})
        speaker.control_behavior = {
            "circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": False}
        }
        speaker.signal_value_is_pitch = None
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        with self.assertRaises(TypeError):
            speaker.signal_value_is_pitch = "incorrect"

    def test_set_instrument_id(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(speaker.instrument_id, None)
        speaker.instrument_id = 0
        self.assertEqual(speaker.instrument_id, 0)
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        speaker.instrument_id = 0
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        speaker.instrument_id = None
        self.assertEqual(speaker.control_behavior, {})
        speaker.signal_value_is_pitch = True
        speaker.instrument_id = None
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"signal_value_is_pitch": True}},
        )

        with self.assertRaises(InvalidInstrumentID):
            speaker.instrument_id = 100
        with self.assertRaises(TypeError):
            speaker.instrument_id = TypeError

    def test_set_instrument_name(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(speaker.instrument_name, None)
        speaker.instrument_name = "alarms"
        self.assertEqual(speaker.instrument_name, "alarms")
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        speaker.instrument_name = "alarms"
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        speaker.instrument_name = None
        self.assertEqual(speaker.control_behavior, {})
        speaker.signal_value_is_pitch = True
        speaker.instrument_name = None
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"signal_value_is_pitch": True}},
        )
        with self.assertRaises(InvalidInstrumentID):
            speaker.instrument_name = "incorrect"
        with self.assertRaises(TypeError):
            speaker.instrument_name = TypeError

    def test_set_note_id(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(speaker.note_id, None)
        with self.assertRaises(DraftsmanError):
            speaker.note_id = 0
        speaker.instrument_name = "alarms"
        speaker.note_id = 0
        self.assertEqual(speaker.note_id, 0)
        self.assertEqual(speaker.note_name, "alarm-1")
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"instrument_id": 0, "note_id": 0}},
        )
        speaker.note_id = 1
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"instrument_id": 0, "note_id": 1}},
        )
        speaker.note_id = None
        self.assertEqual(
            speaker.control_behavior, {"circuit_parameters": {"instrument_id": 0}}
        )
        speaker.signal_value_is_pitch = True
        speaker.note_id = None
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": True}},
        )

        with self.assertRaises(InvalidNoteID):
            speaker.note_id = 100
        with self.assertRaises(TypeError):
            speaker.note_id = TypeError

    def test_set_note_name(self):
        speaker = ProgrammableSpeaker()
        self.assertEqual(speaker.note_name, None)
        with self.assertRaises(DraftsmanError):
            speaker.note_name = "alarm-1"

        speaker.note_name = None
        self.assertEqual(speaker.note_name, None)
        speaker.instrument_name = "alarms"
        speaker.note_name = "siren"
        self.assertEqual(speaker.note_name, "siren")
        self.assertEqual(speaker.note_id, 6)
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"instrument_id": 0, "note_id": 6}},
        )
        speaker.note_name = None
        self.assertEqual(
            speaker.control_behavior,
            {
                "circuit_parameters": {
                    "instrument_id": 0,
                }
            },
        )
        speaker.signal_value_is_pitch = True
        speaker.note_name = None
        self.assertEqual(
            speaker.control_behavior,
            {"circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": True}},
        )

        with self.assertRaises(InvalidNoteID):
            speaker.note_name = "incorrect"
        with self.assertRaises(TypeError):
            speaker.note_name = TypeError
