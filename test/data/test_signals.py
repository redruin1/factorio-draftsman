from draftsman.data import signals

import pytest


@pytest.mark.parametrize(
    "i,signal_type,signal_location",
    [
        (1, "item", signals.item),
        (2, "fluid", signals.fluid),
        (3, "recipe", signals.recipe),
        (4, "entity", signals.entity),
        (5, "space-location", signals.space_location),
        (6, "asteroid-chunk", signals.asteroid_chunk),
        (7, "quality", signals.quality),
        (8, "virtual", signals.virtual),
    ],
)
def test_add_signal(i, signal_type, signal_location):
    """
    Ensure adding a signal (of any type) properly populates all relevant data
    structures.
    """
    signal_name = "new-signal-" + str(i)
    print(signal_name)
    signals.add_signal(signal_name, signal_type)
    assert signals.raw[signal_name] == {"name": signal_name, "type": signal_type}
    assert signals.type_of[signal_name] == [signal_type]
    assert signal_name in signal_location


def test_add_signal_incorrect_type():
    """
    Make sure attempting to add a signal of unknown type results in an error.
    """
    with pytest.raises(ValueError):
        signals.add_signal("new-signal", "incorrect")
