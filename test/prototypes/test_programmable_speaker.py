# test_programmable_speaker.py

from draftsman.constants import ValidationMode
from draftsman.entity import ProgrammableSpeaker, programmable_speakers, Container
from draftsman.error import (
    DraftsmanError,
    InvalidEntityError,
    InvalidSignalError,
    InvalidInstrumentID,
    InvalidNoteID,
    DataFormatError,
    IncompleteSignalError,
)
from draftsman.signatures import SignalID, Condition
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownInstrumentWarning,
    UnknownNoteWarning,
    UnknownSignalWarning,
    VolumeRangeWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_programmable_speaker():
    if len(programmable_speakers) == 0:
        return None
    return ProgrammableSpeaker(
        "programmable-speaker",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        volume=1.0,
        circuit_enabled=True,
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        global_playback=True,
        allow_polyphony=True,
        show_alert=True,
        show_alert_on_map=False,
        alert_icon="signal-check",
        alert_message="some string",
        signal_value_is_pitch=False,
        instrument_id=1,
        note_id=1,
        tags={"blah": "blah"},
    )


class TestProgrammableSpeakerTesting:
    def test_constructor_init(self):
        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            tile_position=[10, 10],
            volume=1.0,
            global_playback=True,
            allow_polyphony=True,
            show_alert=True,
            show_alert_on_map=False,
            alert_icon="signal-check",
            alert_message="some string",
            signal_value_is_pitch=False,
            instrument_id=1,
            note_id=1,
        )
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 10.5, "y": 10.5},
            "parameters": {
                # "playback_volume": 1.0, # Default
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
                    # "signal_value_is_pitch": False, # Default
                    "instrument_id": 1,
                    "note_id": 1,
                }
            },
        }

        speaker = ProgrammableSpeaker(
            "programmable-speaker",
            tile_position=[10, 10],
            volume=1.0,
            global_playback=True,
            allow_polyphony=True,
            show_alert=True,
            show_alert_on_map=False,
            alert_icon={"name": "signal-check", "type": "virtual"},
            alert_message="some string",
            signal_value_is_pitch=False,
            instrument_id=1,
            note_id=1,
        )
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 10.5, "y": 10.5},
            "parameters": {
                # "playback_volume": 1.0, # Default
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
                    # "signal_value_is_pitch": False, # Default
                    "instrument_id": 1,
                    "note_id": 1,
                }
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            ProgrammableSpeaker.from_dict(
                {"name": "programmable-speaker", "unused_keyword": "whatever"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            ProgrammableSpeaker("not a programmable speaker").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            ProgrammableSpeaker(tags="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
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

    def test_set_volume(self):
        speaker = ProgrammableSpeaker()
        speaker.volume = 0.5
        assert speaker.volume == 0.5

        # No warning
        speaker.volume = 10.0
        assert speaker.volume == 10.0

        # Only warns on PEDANTIC
        speaker.validate_assignment = ValidationMode.PEDANTIC

        speaker.volume = 0.5
        assert speaker.volume == 0.5

        with pytest.warns(VolumeRangeWarning):
            speaker.volume = 10.0
        assert speaker.volume == 10.0

        # No Error
        speaker.validate_assignment = "none"
        speaker.volume = "incorrect"
        assert speaker.volume == "incorrect"

        # Error
        speaker.validate_assignment = "strict"
        with pytest.raises(DataFormatError):
            speaker.volume = "incorrect"

    def test_set_global_playback(self):
        speaker = ProgrammableSpeaker()
        assert speaker.global_playback == False

        speaker.global_playback = True
        assert speaker.global_playback == True

        # Error
        with pytest.raises(DataFormatError):
            speaker.global_playback = "incorrect"

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.global_playback = "incorrect"
        assert speaker.global_playback == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "parameters": {"playback_globally": "incorrect"},
        }

    def test_set_show_alert(self):
        speaker = ProgrammableSpeaker()
        assert speaker.show_alert == False

        speaker.show_alert = True
        assert speaker.show_alert == True

        # Error
        with pytest.raises(DataFormatError):
            speaker.show_alert = "incorrect"

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.show_alert = "incorrect"
        assert speaker.show_alert == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "alert_parameters": {"show_alert": "incorrect"},
        }

    def test_set_polyphony(self):
        speaker = ProgrammableSpeaker()
        assert speaker.allow_polyphony == False

        speaker.allow_polyphony = True
        assert speaker.allow_polyphony == True

        # Error
        with pytest.raises(DataFormatError):
            speaker.allow_polyphony = "incorrect"

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.allow_polyphony = "incorrect"
        assert speaker.allow_polyphony == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "parameters": {"allow_polyphony": "incorrect"},
        }

    def test_set_show_alert_on_map(self):
        speaker = ProgrammableSpeaker()
        assert speaker.show_alert_on_map == True

        speaker.show_alert_on_map = False
        assert speaker.show_alert_on_map == False

        # Error
        with pytest.raises(DataFormatError):
            speaker.show_alert_on_map = "incorrect"

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.show_alert_on_map = "incorrect"
        assert speaker.show_alert_on_map == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "alert_parameters": {"show_on_map": "incorrect"},
        }

    def test_set_alert_icon(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_icon = "signal-check"
        assert speaker.alert_icon == SignalID(name="signal-check", type="virtual")

        speaker.alert_icon = {"name": "signal-check", "type": "virtual"}
        assert speaker.alert_icon == SignalID(name="signal-check", type="virtual")

        speaker.alert_icon = None
        assert speaker.alert_icon == None

        with pytest.warns(UnknownSignalWarning):
            speaker.alert_icon = {"name": "unknown", "type": "virtual"}
            assert speaker.alert_icon == SignalID(name="unknown", type="virtual")

        with pytest.raises(DataFormatError):
            speaker.alert_icon = TypeError
        with pytest.raises(IncompleteSignalError):
            speaker.alert_icon = "incorrect"

    def test_set_alert_message(self):
        speaker = ProgrammableSpeaker()
        speaker.alert_message = "some string"
        assert speaker.alert_message == "some string"

        speaker.alert_message = None
        assert speaker.alert_message == ""

        with pytest.raises(DataFormatError):
            speaker.alert_message = False

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.alert_message = False
        assert speaker.alert_message == False
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "alert_parameters": {"alert_message": False},
        }

    def test_set_signal_value_is_pitch(self):
        speaker = ProgrammableSpeaker()
        assert speaker.signal_value_is_pitch == False

        speaker.signal_value_is_pitch = True
        assert speaker.signal_value_is_pitch == True

        with pytest.raises(DataFormatError):
            speaker.signal_value_is_pitch = "incorrect"

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.signal_value_is_pitch = "incorrect"
        assert speaker.signal_value_is_pitch == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "circuit_parameters": {"signal_value_is_pitch": "incorrect"}
            },
        }

    def test_set_instrument_id(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instrument_id == 0
        assert speaker.instrument_name == "alarms"

        speaker.instrument_id = 1
        assert speaker.instrument_id == 1
        assert speaker.instrument_name == "miscellaneous"

        speaker.instrument_id = None
        assert speaker.instrument_id == None
        assert speaker.instrument_name == None

        # Warnings
        with pytest.warns(UnknownInstrumentWarning):
            speaker.instrument_id = 100
        assert speaker.instrument_id == 100

        # No warnings
        speaker.validate_assignment = ValidationMode.MINIMUM
        speaker.instrument_id = 100
        assert speaker.instrument_id == 100

        # Errors
        with pytest.raises(DataFormatError):
            speaker.instrument_id = TypeError

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.instrument_id = "incorrect"
        assert speaker.instrument_id == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_parameters": {"instrument_id": "incorrect"}},
        }

        # Test validation with unknown programmable speaker
        unknown = ProgrammableSpeaker(
            "programmable-speaker-2", validate_assignment="none"
        )
        unknown.instrument_id = 10
        assert unknown.instrument_id == 10

    def test_set_instrument_name(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instrument_name == "alarms"
        assert speaker.instrument_id == 0

        speaker.instrument_name = "miscellaneous"
        assert speaker.instrument_name == "miscellaneous"
        assert speaker.instrument_id == 1

        speaker.instrument_name = None
        assert speaker.instrument_name == None
        assert speaker.instrument_id == None

        # Warnings
        with pytest.warns(UnknownInstrumentWarning):
            speaker.instrument_name = "incorrect"
        assert speaker.instrument_id == None
        # Here the instrument name is not even set, which is because we have no
        # way of knowing the translation of this string to an integer index
        # since it was unrecognized
        # If you want to use unknown instruments, use `instrument_id` instead
        # and translate yourself
        assert speaker.instrument_name == None

    def test_set_note_id(self):
        speaker = ProgrammableSpeaker()
        assert speaker.note_id == 0

        speaker.instrument_name = "alarms"
        speaker.note_id = 0
        assert speaker.note_id == 0
        assert speaker.note_name == "alarm-1"

        speaker.note_id = 1
        assert speaker.note_id == 1
        assert speaker.note_name == "alarm-2"

        speaker.note_id = None
        assert speaker.note_id == None
        assert speaker.note_name == None
        assert speaker.instrument_id == 0
        assert speaker.instrument_name == "alarms"

        # Warnings
        with pytest.warns(UnknownNoteWarning):
            speaker.note_id = 100
        assert speaker.note_id == 100
        assert speaker.note_name == None

        # No warning
        speaker.validate_assignment = "minimum"
        assert speaker.validate_assignment is ValidationMode.MINIMUM
        speaker.note_id = 100
        assert speaker.note_id == 100

        speaker.validate_assignment = "strict"
        # Handle the case where the instrument is unknown
        with pytest.warns(UnknownInstrumentWarning):
            speaker.instrument_id = 100

        speaker.note_id = 100
        assert speaker.note_id == 100

        # Reset
        speaker.instrument_id = None

        # Errors
        with pytest.raises(DataFormatError):
            speaker.note_id = TypeError

        # No error
        speaker.validate_assignment = "none"
        assert speaker.validate_assignment == ValidationMode.NONE

        speaker.note_id = "incorrect"
        assert speaker.note_id == "incorrect"
        assert speaker.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_parameters": {"note_id": "incorrect"}},
        }

    def test_set_note_name(self):
        speaker = ProgrammableSpeaker()
        assert speaker.instrument_id == 0
        assert speaker.instrument_name == "alarms"
        assert speaker.note_id == 0
        assert speaker.note_name == "alarm-1"

        speaker.note_name = "alarm-2"
        assert speaker.note_id == 1
        assert speaker.note_name == "alarm-2"

        speaker.note_name = "siren"
        assert speaker.note_id == 6
        assert speaker.note_name == "siren"

        speaker.note_name = None
        assert speaker.note_name == None
        assert speaker.note_id == None
        assert speaker.instrument_name == "alarms"
        assert speaker.instrument_id == 0

        # Warnings
        with pytest.warns(UnknownNoteWarning):
            speaker.note_name = "incorrect"
        assert speaker.note_id == None
        # Here the note name is not even set, which is because we have no
        # way of knowing the translation of this string to an integer index
        # since it was unrecognized
        # If you want to use unknown notes, use `note_id` instead and translate
        # yourself
        assert speaker.note_name == None

        # Handle the case where the instrument is unknown
        with pytest.warns(UnknownInstrumentWarning):
            speaker.instrument_id = 100

        with pytest.warns(UnknownNoteWarning):
            speaker.note_name = "unknown"
        assert speaker.note_name == None

    def test_mergable_with(self):
        speaker1 = ProgrammableSpeaker("programmable-speaker")
        speaker2 = ProgrammableSpeaker(
            "programmable-speaker",
            volume=1.0,
            global_playback=True,
            allow_polyphony=True,
            show_alert=True,
            show_alert_on_map=False,
            alert_icon="signal-check",
            alert_message="some string",
            signal_value_is_pitch=False,
            instrument_id=1,
            note_id=1,
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
            volume=0.5,
            global_playback=True,
            allow_polyphony=True,
            show_alert=True,
            show_alert_on_map=False,
            alert_icon="signal-check",
            alert_message="some string",
            signal_value_is_pitch=True,
            instrument_id=1,
            note_id=1,
            tags={"some": "stuff"},
        )

        speaker1.merge(speaker2)
        del speaker2

        assert speaker1.volume == 0.5
        assert speaker1.global_playback == True
        assert speaker1.allow_polyphony == True
        assert speaker1.show_alert == True
        assert speaker1.show_alert_on_map == False
        assert speaker1.alert_icon == SignalID(name="signal-check", type="virtual")
        assert speaker1.alert_message == "some string"
        assert speaker1.signal_value_is_pitch == True
        assert speaker1.instrument_id == 1
        assert speaker1.note_id == 1
        assert speaker1.tags == {"some": "stuff"}

        assert speaker1.to_dict() == {
            "name": "programmable-speaker",
            "position": {"x": 0.5, "y": 0.5},
            "parameters": {
                "playback_volume": 0.5,
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
                    "signal_value_is_pitch": True,
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
