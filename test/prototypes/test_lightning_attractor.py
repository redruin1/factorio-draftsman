# test_lightning_attractor.py

from draftsman.prototypes.container import Container
from draftsman.prototypes.lightning_attractor import (
    LightningAttractor,
    lightning_attractors,
)
from draftsman.warning import UnknownEntityWarning

import pytest
from typing import Hashable


def test_constructor():
    attractor = LightningAttractor("lightning-rod")

    with pytest.warns(UnknownEntityWarning):
        LightningAttractor("unknown lightning attractor")


def test_flags():
    for tower_name in lightning_attractors:
        tower = LightningAttractor(tower_name)
        assert tower.power_connectable == False
        assert tower.dual_power_connectable == False
        assert tower.circuit_connectable == False
        assert tower.dual_circuit_connectable == False


def test_eq():
    attractor1 = LightningAttractor("lightning-rod")
    attractor2 = LightningAttractor("lightning-rod")

    assert attractor1 == attractor2

    attractor1.tags = {"some": "stuff"}

    assert attractor1 != attractor2

    container = Container()

    assert attractor1 != container
    assert attractor2 != container

    # hashable
    assert isinstance(attractor1, Hashable)