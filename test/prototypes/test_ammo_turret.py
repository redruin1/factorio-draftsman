# test_ammo_turret.py

from draftsman.entity import AmmoTurret, ammo_turrets, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestAmmoTurret:
    def test_constructor_init(self):
        turret = AmmoTurret("gun-turret")
        turret.validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            turret = AmmoTurret("this is not a turret")
            turret.validate().reissue_all()

    def test_flags(self):
        turret = AmmoTurret("gun-turret")
        assert turret.rotatable == True
        assert turret.square == True
        # TODO: move
        # turret = AmmoTurret("flamethrower-turret")
        # assert turret.rotatable == True
        # assert turret.square == False

    def test_mergable_with(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        assert turret1.mergable_with(turret1)

        assert turret1.mergable_with(turret2)
        assert turret2.mergable_with(turret1)

        turret2.tile_position = (1, 1)
        assert not turret1.mergable_with(turret2)

    def test_merge(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        turret1.merge(turret2)
        del turret2

        assert turret1.tags == {"some": "stuff"}

    def test_eq(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret")

        assert turret1 == turret2

        turret1.tags = {"some": "stuff"}

        assert turret1 != turret2

        container = Container()

        assert turret1 != container
        assert turret2 != container

        # hashable
        assert isinstance(turret1, Hashable)
