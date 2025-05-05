# test_car.py

from draftsman.prototypes.car import (
    Car,
    cars,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    car = Car("car")

    with pytest.warns(UnknownEntityWarning):
        Car("this is not a car")


def test_flags():
    for car_name in cars:
        car = Car(car_name)
        assert car.power_connectable == False
        assert car.dual_power_connectable == False
        assert car.circuit_connectable == False
        assert car.dual_circuit_connectable == False