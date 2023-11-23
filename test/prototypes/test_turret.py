# test_turret.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Turret, turrets, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestTurret:
    def test_constructor_init(self):
        turret = Turret("gun-turret")

        with pytest.warns(UnknownKeywordWarning):
            Turret("gun-turret", unused_keyword="whatever")

        with pytest.warns(UnknownEntityWarning):
            Turret("this is not a turret")

    def test_flags(self):
        turret = Turret("gun-turret")
        assert turret.rotatable == True
        assert turret.square == True
        turret = Turret("flamethrower-turret")
        assert turret.rotatable == True
        assert turret.square == False

    def test_mergable_with(self):
        turret1 = Turret("gun-turret")
        turret2 = Turret("gun-turret", tags={"some": "stuff"})

        assert turret1.mergable_with(turret1)

        assert turret1.mergable_with(turret2)
        assert turret2.mergable_with(turret1)

        turret2.tile_position = (1, 1)
        assert not turret1.mergable_with(turret2)

    def test_merge(self):
        turret1 = Turret("gun-turret")
        turret2 = Turret("gun-turret", tags={"some": "stuff"})

        turret1.merge(turret2)
        del turret2

        assert turret1.tags == {"some": "stuff"}

    def test_eq(self):
        turret1 = Turret("gun-turret")
        turret2 = Turret("gun-turret")

        assert turret1 == turret2

        turret1.tags = {"some": "stuff"}

        assert turret1 != turret2

        container = Container()

        assert turret1 != container
        assert turret2 != container

        # hashable
        assert isinstance(turret1, Hashable)
