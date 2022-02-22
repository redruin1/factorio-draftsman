# test_storagetank.py

from draftsman.entity import StorageTank, storage_tanks

from unittest import TestCase

class StorageTankTesting(TestCase):
    def test_default_constructor(self):
        storage_tank = StorageTank()
        self.assertEqual(
            storage_tank.to_dict(),
            {
                "name": storage_tanks[0],
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_constructor(self):
        pass

    def test_circuit_connections(self):
        pass