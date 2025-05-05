# test_rail_support.py

from draftsman.prototypes.rail_support import (
    RailSupport,
    rail_supports,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    support = RailSupport("rail-support")

    with pytest.warns(UnknownEntityWarning):
        RailSupport("unknown rail support")


def test_flags():
    for support_name in rail_supports:
        support = RailSupport(support_name)
        assert support.power_connectable == False
        assert support.dual_power_connectable == False
        assert support.circuit_connectable == False
        assert support.dual_circuit_connectable == False