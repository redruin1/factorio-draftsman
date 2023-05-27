# test_train_configuration.py

from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.prototypes.locomotive import Locomotive
from draftsman.prototypes.cargo_wagon import CargoWagon
from draftsman.prototypes.fluid_wagon import FluidWagon
from draftsman.prototypes.artillery_wagon import ArtilleryWagon

import pytest


class TestTrainConfiguration:
    def test_constructor(self):
        # Default
        tc = TrainConfiguration()
        assert tc.cars == []
        assert tc.rail_length == 0

        # Valid string
        tc = TrainConfiguration("1-4-1")
        assert len(tc.cars) == 6
        assert tc.cars == [
            Locomotive("locomotive", orientation=0),
            CargoWagon("cargo-wagon"),
            CargoWagon("cargo-wagon"),
            CargoWagon("cargo-wagon"),
            CargoWagon("cargo-wagon"),
            Locomotive("locomotive", orientation=0.5),
        ]

        # Invalid string
        with pytest.raises(ValueError, match="Encountered unexpected character 'W'"):
            tc = TrainConfiguration("wrong")

    def test_from_string(self):
        tc = TrainConfiguration()
        tc.from_string("2-4-2", direction="forward", wagons="artillery")
        assert len(tc.cars) == 8
        assert tc.cars == [
            Locomotive("locomotive", orientation=0),
            Locomotive("locomotive", orientation=0),
            ArtilleryWagon("artillery-wagon"),
            ArtilleryWagon("artillery-wagon"),
            ArtilleryWagon("artillery-wagon"),
            ArtilleryWagon("artillery-wagon"),
            Locomotive("locomotive", orientation=0),
            Locomotive("locomotive", orientation=0),
        ]

        # Partially correct
        with pytest.raises(ValueError, match="Encountered unexpected character 'D'"):
            tc.from_string("<CFAD")

        # Invalid direction
        with pytest.raises(
            ValueError, match="Argument 'direction' must be one of 'dual' or 'forward'"
        ):
            tc.from_string("2-4-2", direction="incorrect value")

        # Invalid wagons
        with pytest.raises(
            ValueError,
            match="Argument 'wagons' must be one of 'cargo', 'fluid', or 'artillery'",
        ):
            tc.from_string("2-4-2", wagons="incorrect value")
