# test_burner_generator.py

from draftsman.constants import ValidationMode
from draftsman.entity import BurnerGenerator, burner_generators, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import (
    FuelCapacityWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestBurnerGenerator:
    def test_contstructor_init(self):
        generator = BurnerGenerator("burner-generator")

        with pytest.warns(UnknownKeywordWarning):
            BurnerGenerator(unused_keyword="whatever").validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            BurnerGenerator("this is not a burner generator").validate().reissue_all()

    def test_set_items(self):
        generator = BurnerGenerator("burner-generator")
        assert generator.allowed_fuel_items == {
            "biter-egg",
            "carbon",
            "coal",
            "jelly",
            "jellynut",
            "jellynut-seed",
            "nuclear-fuel",
            "pentapod-egg",
            "rocket-fuel",
            "solid-fuel",
            "spoilage",
            "tree-seed",
            "wood",
            "yumako",
            "yumako-mash",
            "yumako-seed",
        }

        generator.set_item_request("coal", 50)
        assert generator.items == {"coal": 50}

        with pytest.warns(ItemLimitationWarning):
            generator.items = {"iron-plate": 1000}
        assert generator.items == {"iron-plate": 1000}

        with pytest.warns(FuelCapacityWarning):
            generator.set_item_request("coal", 200)
        assert generator.items == {"coal": 200, "iron-plate": 1000}

        generator.validate_assignment = "minimum"
        assert generator.validate_assignment == ValidationMode.MINIMUM

        generator.items = {"coal": 200, "iron-plate": 1000}
        assert generator.items == {"coal": 200, "iron-plate": 1000}

        # Ensure that validating without a custom context doesn't break it
        BurnerGenerator.Format.model_validate(generator._root)

    def test_mergable_with(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        assert generator1.mergable_with(generator2)
        assert generator2.mergable_with(generator1)

        generator2.tile_position = [-10, -10]
        assert not generator1.mergable_with(generator2)

    def test_merge(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        generator1.merge(generator2)
        del generator2

        assert generator1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
