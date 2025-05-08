# test_signatures.py

from draftsman.signatures import AttrsSignalID
from draftsman.warning import UnknownSignalWarning

import pytest


def test_signal_id():
    # Test correct default different signal types
    id = AttrsSignalID(name="steam")
    assert id == AttrsSignalID(name="steam", type="fluid")
    id = AttrsSignalID(name="signal-A")
    assert id == AttrsSignalID(name="signal-A", type="virtual")

    # Test defaulting type back to item when signal not recognized
    with pytest.warns(UnknownSignalWarning):
        id = AttrsSignalID("unknown signal")
        assert id == AttrsSignalID(name="unknown signal", type="item")