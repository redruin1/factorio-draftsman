# test_instruments

from draftsman.data import instruments
from draftsman.entity import ProgrammableSpeaker
from draftsman.warning import UnknownNoteWarning

import pytest


class TestInstrumentData:
    def test_add_instrument(self):
        # Unknown entity
        with pytest.raises(TypeError):
            instruments.add_instrument(
                instrument_name="new-instrument",
                notes=["A", "B", "C"],
                entity_name="unknown",
            )
        # Known entity, but not a programmable speaker
        with pytest.raises(TypeError):
            instruments.add_instrument(
                instrument_name="new-instrument",
                notes=["A", "B", "C"],
                entity_name="wooden-chest",
            )

        instruments.add_instrument(
            instrument_name="new-instrument", notes=["A", "B", "C"]
        )
        assert instruments.raw["programmable-speaker"][-1] == {
            "name": "new-instrument",
            "notes": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
        }
        assert len(instruments.raw["programmable-speaker"]) == 13
        assert instruments.index_of["programmable-speaker"]["new-instrument"] == {
            "self": 12,
            "A": 0,
            "B": 1,
            "C": 2,
        }
        assert instruments.name_of["programmable-speaker"][12] == {
            "self": "new-instrument",
            0: "A",
            1: "B",
            2: "C",
        }

        # Test setting an actual ProgrammableSpeaker with this new instrument
        speaker = ProgrammableSpeaker("programmable-speaker")

        speaker.instrument_name = "new-instrument"
        assert speaker.instrument_name == "new-instrument"
        assert speaker.instrument_id == 12

        speaker.note_name = "A"
        assert speaker.note_name == "A"
        assert speaker.note_id == 0

        with pytest.warns(UnknownNoteWarning):
            speaker.note_name = "D"
        assert speaker.note_name == None
        assert speaker.note_id == None
