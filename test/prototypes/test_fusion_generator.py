# test_fusion_generator.py

from draftsman.prototypes.fusion_generator import (
    FusionGenerator,
    fusion_generators,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    generator = FusionGenerator("fusion-generator")

    with pytest.warns(UnknownEntityWarning):
        FusionGenerator("unknown fusion generator")


def test_flags():
    for generator_name in fusion_generators:
        generator = FusionGenerator(generator_name)
        assert generator.power_connectable == False
        assert generator.dual_power_connectable == False
        assert generator.circuit_connectable == False
        assert generator.dual_circuit_connectable == False
