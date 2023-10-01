# test_programmable_speaker.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ProgrammableSpeaker, programmable_speakers, Container
from draftsman.error import (
    DraftsmanError,
    InvalidEntityError,
    InvalidSignalError,
    InvalidInstrumentID,
    InvalidNoteID,
    DataFormatError,
)
from draftsman.warning import DraftsmanWarning, VolumeRangeWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ProgrammableSpeakerTesting(unittest.TestCase):
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
        assert speaker.to_dict() == {
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
        }

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
        assert speaker.to_dict() == {
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
        }

        speaker = ProgrammableSpeaker(control_behavior={"circuit_enable_disable": True})
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_enable_disable": True},
        }
        speaker = ProgrammableSpeaker(
            control_behavior={"circuit_parameters": {"signal_value_is_pitch": True}}
        )
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_parameters": {"signal_value_is_pitch": True}},
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            ProgrammableSpeaker(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            ProgrammableSpeaker("not a programmable speaker")
        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     ProgrammableSpeaker(control_behavior={"unused_key": "something"})

    def test_flags(self):
        for name in programmable_speakers:
            speaker = ProgrammableSpeaker(name)
            assert speaker.power_connectable == False
            assert speaker.dual_power_connectable == False
            assert speaker.circuit_connectable == True
            assert speaker.dual_circuit_connectable == False

    def test_get_instruments(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instruments["alarms"] == {
            "alarm-1",
            "alarm-2",
            "buzzer-1",
            "buzzer-2",
            "buzzer-3",
            "ring",
            "siren",
        }

    def test_set_parameters(self):
        speaker = ProgrammableSpeaker()
        speaker.parameters = None
        assert speaker.parameters == {}

        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     speaker.parameters = "false"

    def test_set_alert_parameters(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_parameters = None
        assert speaker.alert_parameters == {}

        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     speaker.alert_parameters = "false"

    def test_set_volume(self):
        speaker = ProgrammableSpeaker()
        speaker.volume = 0.5
        assert speaker.volume == 0.5
        assert speaker.parameters == {"playback_volume": 0.5}
        speaker.volume = None
        assert speaker.parameters == {}

        # Warnings
        # TODO: move to inspect
        # with pytest.warns(VolumeRangeWarning):
        #     speaker.volume = 10.0
        # assert speaker.parameters == {"playback_volume": 10.0}

        # No Error
        speaker.volume = "incorrect"
        assert speaker.parameters == {"playback_volume": "incorrect"}

    def test_set_global_playback(self):
        speaker = ProgrammableSpeaker()
        speaker.global_playback = True
        assert speaker.global_playback == True
        assert speaker.parameters == {"playback_globally": True}
        speaker.global_playback = None
        assert speaker.parameters == {}
        with pytest.raises(TypeError):
            speaker.global_playback = "incorrect"

    def test_set_show_alert(self):
        speaker = ProgrammableSpeaker()
        speaker.show_alert = True
        assert speaker.show_alert == True
        assert speaker.alert_parameters == {"show_alert": True}
        speaker.show_alert = None
        assert speaker.alert_parameters == {}
        with pytest.raises(TypeError):
            speaker.show_alert = "incorrect"

    def test_set_polyphony(self):
        speaker = ProgrammableSpeaker()
        speaker.allow_polyphony = True
        assert speaker.allow_polyphony == True
        assert speaker.parameters == {"allow_polyphony": True}
        speaker.allow_polyphony = None
        assert speaker.parameters == {}
        with pytest.raises(TypeError):
            speaker.allow_polyphony = "incorrect"

    def test_set_show_alert_on_map(self):
        speaker = ProgrammableSpeaker()
        speaker.show_alert_on_map = True
        assert speaker.show_alert_on_map == True
        assert speaker.alert_parameters == {"show_on_map": True}
        speaker.show_alert_on_map = None
        assert speaker.alert_parameters == {}
        with pytest.raises(TypeError):
            speaker.show_alert_on_map = "incorrect"

    def test_set_alert_icon(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_icon = "signal-check"
        assert speaker.alert_icon == {"name": "signal-check", "type": "virtual"}
        assert speaker.alert_parameters == {
            "icon_signal_id": {"name": "signal-check", "type": "virtual"}
        }
        speaker.alert_icon = {"name": "signal-check", "type": "virtual"}
        assert speaker.alert_parameters == {
            "icon_signal_id": {"name": "signal-check", "type": "virtual"}
        }
        speaker.alert_icon = None
        assert speaker.alert_parameters == {}
        with pytest.raises(TypeError):
            speaker.alert_icon = TypeError
        with pytest.raises(InvalidSignalError):
            speaker.alert_icon = "incorrect"

    def test_set_alert_message(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_message = "some string"
        assert speaker.alert_message == "some string"
        assert speaker.alert_parameters == {"alert_message": "some string"}
        speaker.alert_message = None
        assert speaker.alert_parameters == {}
        with pytest.raises(TypeError):
            speaker.alert_message = False

    def test_set_signal_value_is_pitch(self):
        speaker = ProgrammableSpeaker()
        assert speaker.signal_value_is_pitch == None
        speaker.signal_value_is_pitch = True
        assert speaker.signal_value_is_pitch == True
        assert speaker.control_behavior == {
            "circuit_parameters": {"signal_value_is_pitch": True}
        }
        speaker.signal_value_is_pitch = None
        assert speaker.control_behavior == {}
        speaker.control_behavior = {
            "circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": False}
        }
        speaker.signal_value_is_pitch = None
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        with pytest.raises(TypeError):
            speaker.signal_value_is_pitch = "incorrect"

    def test_set_instrument_id(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instrument_id == None
        speaker.instrument_id = 0
        assert speaker.instrument_id == 0
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        speaker.instrument_id = 0
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        speaker.instrument_id = None
        assert speaker.control_behavior == {}
        speaker.signal_value_is_pitch = True
        speaker.instrument_id = None
        assert speaker.control_behavior == {
            "circuit_parameters": {"signal_value_is_pitch": True}
        }

        with pytest.raises(InvalidInstrumentID):
            speaker.instrument_id = 100
        with pytest.raises(TypeError):
            speaker.instrument_id = TypeError

    def test_set_instrument_name(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instrument_name == None
        speaker.instrument_name = "alarms"
        assert speaker.instrument_name == "alarms"
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        speaker.instrument_name = "alarms"
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        speaker.instrument_name = None
        assert speaker.control_behavior == {}
        speaker.signal_value_is_pitch = True
        speaker.instrument_name = None
        assert speaker.control_behavior == {
            "circuit_parameters": {"signal_value_is_pitch": True}
        }
        with pytest.raises(InvalidInstrumentID):
            speaker.instrument_name = "incorrect"
        with pytest.raises(TypeError):
            speaker.instrument_name = TypeError

    def test_set_note_id(self):
        speaker = ProgrammableSpeaker()
        assert speaker.note_id == None
        with pytest.raises(DraftsmanError):
            speaker.note_id = 0
        speaker.instrument_name = "alarms"
        speaker.note_id = 0
        assert speaker.note_id == 0
        assert speaker.note_name == "alarm-1"
        assert speaker.control_behavior == {
            "circuit_parameters": {"instrument_id": 0, "note_id": 0}
        }
        speaker.note_id = 1
        assert speaker.control_behavior == {
            "circuit_parameters": {"instrument_id": 0, "note_id": 1}
        }
        speaker.note_id = None
        assert speaker.control_behavior == {"circuit_parameters": {"instrument_id": 0}}
        speaker.signal_value_is_pitch = True
        speaker.note_id = None
        assert speaker.control_behavior == {
            "circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": True}
        }

        with pytest.raises(InvalidNoteID):
            speaker.note_id = 100
        with pytest.raises(TypeError):
            speaker.note_id = TypeError

    def test_set_note_name(self):
        speaker = ProgrammableSpeaker()
        assert speaker.note_name == None
        with pytest.raises(DraftsmanError):
            speaker.note_name = "alarm-1"

        speaker.note_name = None
        assert speaker.note_name == None
        speaker.instrument_name = "alarms"
        speaker.note_name = "siren"
        assert speaker.note_name == "siren"
        assert speaker.note_id == 6
        assert speaker.control_behavior == {
            "circuit_parameters": {"instrument_id": 0, "note_id": 6}
        }
        speaker.note_name = None
        assert speaker.control_behavior == {
            "circuit_parameters": {
                "instrument_id": 0,
            }
        }
        speaker.signal_value_is_pitch = True
        speaker.note_name = None
        assert speaker.control_behavior == {
            "circuit_parameters": {"instrument_id": 0, "signal_value_is_pitch": True}
        }

        with pytest.raises(InvalidNoteID):
            speaker.note_name = "incorrect"
        with pytest.raises(TypeError):
            speaker.note_name = TypeError

    def test_mergable_with(self):
        speaker1 = ProgrammableSpeaker("programmable-speaker")
        speaker2 = ProgrammableSpeaker(
            "programmable-speaker",
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
            tags={"some": "stuff"},
        )

        assert speaker1.mergable_with(speaker1)

        assert speaker1.mergable_with(speaker2)
        assert speaker2.mergable_with(speaker1)

        speaker2.tile_position = (1, 1)
        assert not speaker1.mergable_with(speaker2)

    def test_merge(self):
        speaker1 = ProgrammableSpeaker("programmable-speaker")
        speaker2 = ProgrammableSpeaker(
            "programmable-speaker",
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
            tags={"some": "stuff"},
        )

        speaker1.merge(speaker2)
        del speaker2

        assert speaker1.volume == 1.0
        assert speaker1.global_playback == True
        assert speaker1.allow_polyphony == True
        assert speaker1.show_alert == True
        assert speaker1.show_alert_on_map == False
        assert speaker1.alert_icon == "signal-check"
        assert speaker1.alert_message == "some string"
        assert speaker1.signal_value_is_pitch == False
        assert speaker1.instrument_id == 1
        assert speaker1.note_id == 1
        assert speaker1.tags == {"some": "stuff"}

        assert speaker1.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
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
            "tags": {"some": "stuff"},
        }

    def test_eq(self):
        speaker1 = ProgrammableSpeaker("programmable-speaker")
        speaker2 = ProgrammableSpeaker("programmable-speaker")

        assert speaker1 == speaker2

        speaker1.tags = {"some": "stuff"}

        assert speaker1 != speaker2

        container = Container()

        assert speaker1 != container
        assert speaker2 != container

        # hashable
        assert isinstance(speaker1, Hashable)
