# test_fusion_reactor.py

from draftsman.prototypes.fusion_reactor import (
    FusionReactor,
    fusion_reactors,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    reactor = FusionReactor("fusion-reactor")

    with pytest.warns(UnknownEntityWarning):
        FusionReactor("unknown fusion reactor")


def test_flags():
    for reactor_name in fusion_reactors:
        reactor = FusionReactor(reactor_name)
        assert reactor.power_connectable == False
        assert reactor.dual_power_connectable == False
        assert reactor.circuit_connectable == False
        assert reactor.dual_circuit_connectable == False
