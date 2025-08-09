# test_signatures.py

from draftsman.signatures import SignalID
from draftsman.warning import UnknownSignalWarning

import pytest


def test_signal_id():
    # Test correct default different signal types
    id = SignalID(name="steam")
    assert id == SignalID(name="steam", type="fluid")
    id = SignalID(name="signal-A")
    assert id == SignalID(name="signal-A", type="virtual")

    # Test defaulting type back to item when signal not recognized
    with pytest.warns(UnknownSignalWarning):
        id = SignalID("unknown signal")
        assert id == SignalID(name="unknown signal", type="item")
