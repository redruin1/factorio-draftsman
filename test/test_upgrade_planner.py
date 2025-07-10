# test_upgrade_planner.py

# from draftsman import mods.versions["base"]
from draftsman.classes.upgrade_planner import (
    UpgradePlanner,
    Mapper,
    UpgradeMapperSource,
    UpgradeMapperDestination,
)
from draftsman.classes.exportable import ValidationResult
from draftsman.constants import ValidationMode
from draftsman.data import entities, items, mods
from draftsman.error import (
    IncorrectBlueprintTypeError,
    MalformedBlueprintStringError,
    DataFormatError,
    InvalidMapperError,
)
from draftsman.signatures import Icon
from draftsman.utils import encode_version
import draftsman.validators
from draftsman.warning import (
    DraftsmanWarning,
    IndexWarning,
    NoEffectWarning,
    UnknownElementWarning,
    UpgradeProhibitedWarning,
)

import pytest
import warnings


class TestUpgradePlanner:
    # test_constructor_cases = deal.cases(UpgradePlanner)

    def test_constructor(self):
        # Empty
        upgrade_planner = UpgradePlanner()
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
        }

        # String
        upgrade_planner = UpgradePlanner.from_string(
            "0eNqrViotSC9KTEmNL8hJzMtLLVKyqlYqTi0pycxLL1ayyivNydFRyixJzVWygqnUhanUUSpLLSrOzM9TsjKyMDQxtzQyNzUDIhOL2loAhpkdww=="
        )
        assert upgrade_planner.extra_keys == None
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(1, 1, 61),
        }

        # Dict
        test_planner = {
            "upgrade_planner": {
                "settings": {
                    "mappers": [
                        {
                            "from": {"name": "transport-belt", "type": "entity"},
                            "to": {"name": "fast-transport-belt", "type": "entity"},
                            "index": 0,
                        }
                    ]
                }
            }
        }
        upgrade_planner = UpgradePlanner.from_dict(test_planner)
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "settings": {
                "mappers": [
                    {
                        "from": {"name": "transport-belt", "type": "entity"},
                        "to": {"name": "fast-transport-belt", "type": "entity"},
                        "index": 0,
                    }
                ]
            },
            "version": encode_version(*mods.versions["base"]),
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            UpgradePlanner.from_dict(
                {"upgrade_planner": {"unused": "keyword"}}
            ).validate().reissue_all()

        # Correct format, but incorrect type
        with pytest.raises(IncorrectBlueprintTypeError):
            UpgradePlanner.from_string(
                "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
            )

        # Incorrect format
        with pytest.raises(MalformedBlueprintStringError):
            UpgradePlanner.from_string("0lmaothisiswrong")

    def test_versioning(self):
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping(
            UpgradeMapperSource(
                type="entity",
                name="transport-belt",
                comparator="<",
                quality="legendary",
            ),
            UpgradeMapperDestination(
                type="entity", name="fast-transport-belt", quality="legendary"
            ),
            index=0,
        )

        assert upgrade_planner.to_dict(version=(1, 0))["upgrade_planner"] == {
            "item": "upgrade-planner",
            "settings": {
                "mappers": [
                    {
                        "index": 0,
                        "from": {"name": "transport-belt", "type": "entity"},
                        "to": {"name": "fast-transport-belt", "type": "entity"},
                    }
                ]
            },
            "version": encode_version(*mods.versions["base"]),
        }
        assert upgrade_planner.to_dict(version=(2, 0))["upgrade_planner"] == {
            "item": "upgrade-planner",
            "settings": {
                "mappers": [
                    {
                        "index": 0,
                        "from": {
                            "name": "transport-belt",
                            "type": "entity",
                            "comparator": "<",
                            "quality": "legendary",
                        },
                        "to": {
                            "name": "fast-transport-belt",
                            "type": "entity",
                            "quality": "legendary",
                        },
                    }
                ]
            },
            "version": encode_version(*mods.versions["base"]),
        }

    def test_description(self):
        upgrade_planner = UpgradePlanner()

        # Normal case
        upgrade_planner.description = "some description"
        assert upgrade_planner.description == "some description"
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
            "settings": {"description": "some description"},
        }

        # None case
        upgrade_planner.description = None
        assert upgrade_planner.description == ""
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
        }

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            upgrade_planner.description = 100
            assert upgrade_planner.description == 100

    def test_icons(self):
        upgrade_planner = UpgradePlanner()

        # Explicit format
        upgrade_planner.icons = [
            Icon(index=0, signal="signal-A")
        ]
        assert upgrade_planner.icons == [
            Icon(index=0, signal="signal-A")
        ]
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
            "settings": {
                "icons": [
                    {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}}
                ]
            },
        }

        # None case
        upgrade_planner.icons = []
        assert upgrade_planner.icons == []
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
        }

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            upgrade_planner.icons = "incorrect"
            assert upgrade_planner.icons == "incorrect"

    def test_set_icons(self):
        upgrade_planner = UpgradePlanner()

        # Single known
        # upgrade_planner.set_icons("signal-A")
        upgrade_planner.icons = ["signal-A"]
        assert upgrade_planner.icons == [
            Icon(index=0, signal="signal-A")
        ]
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
            "settings": {
                "icons": [
                    {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}}
                ]
            },
        }

        # Multiple known
        upgrade_planner.icons = ["signal-A", "signal-B", "signal-C"]
        assert upgrade_planner.icons == [
            Icon(index=0, signal="signal-A"),
            Icon(index=1, signal="signal-B"),
            Icon(index=2, signal="signal-C")
        ]
        assert upgrade_planner.to_dict()["upgrade_planner"] == {
            "item": "upgrade-planner",
            "version": encode_version(*mods.versions["base"]),
            "settings": {
                "icons": [
                    {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}},
                    {"index": 2, "signal": {"name": "signal-B", "type": "virtual"}},
                    {"index": 3, "signal": {"name": "signal-C", "type": "virtual"}},
                ]
            },
        }

        # TODO: errors

    def test_mapper_count(self):
        upgrade_planner = UpgradePlanner()
        assert upgrade_planner.mapper_count == 1000

    def test_mappers(self):
        upgrade_planner = UpgradePlanner()

        # Test full format
        upgrade_planner.mappers = [
            {
                "from": {"name": "transport-belt", "type": "entity"},
                "to": {"name": "fast-transport-belt", "type": "entity"},
                "index": 0,
            },
            {
                "from": {"name": "transport-belt", "type": "entity"},
                "to": {"name": "express-transport-belt", "type": "entity"},
                "index": 23,
            },
        ]
        assert upgrade_planner.mappers == [
            Mapper(
                index=0,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "fast-transport-belt", "type": "entity"},
            ),
            Mapper(
                index=23,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "express-transport-belt", "type": "entity"},
            ),
        ]

        # Test None
        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            upgrade_planner.mappers = "incorrect"
            assert upgrade_planner.mappers == "incorrect"

    def test_set_mapping(self):
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("transport-belt", "fast-transport-belt", 0)
        upgrade_planner.set_mapping("transport-belt", "express-transport-belt", 1)
        assert len(upgrade_planner.mappers) == 2
        assert upgrade_planner.mappers == [
            Mapper(
                index=0,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "fast-transport-belt", "type": "entity"},
            ),
            Mapper(
                index=1,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "express-transport-belt", "type": "entity"},
            ),
        ]

        # Test replace
        upgrade_planner.set_mapping("transport-belt", "fast-transport-belt", 0)
        assert upgrade_planner.mappers == [
            Mapper(
                index=0,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "fast-transport-belt", "type": "entity"},
            ),
            Mapper(
                index=1,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "express-transport-belt", "type": "entity"},
            ),
        ]

        # None as argument values at specified index
        upgrade_planner.set_mapping(None, None, 1)
        assert upgrade_planner.mappers == [
            Mapper(
                index=0,
                from_={"name": "transport-belt", "type": "entity"},
                to={"name": "fast-transport-belt", "type": "entity"},
            ),
            Mapper(index=1, from_=None, to=None),
        ]
        assert upgrade_planner.to_dict()["upgrade_planner"]["settings"]["mappers"] == [
            {
                "from": {"name": "transport-belt", "type": "entity"},
                "to": {"name": "fast-transport-belt", "type": "entity"},
                "index": 0,
            },
            {
                "index": 1,
            },
        ]

        # Errors
        with pytest.raises(DataFormatError):
            upgrade_planner.set_mapping(TypeError, TypeError, TypeError)

        # =====================================================================
        # remove_mapping()
        # =====================================================================

        # Normal
        upgrade_planner.remove_mapping("transport-belt", "fast-transport-belt", 0)
        assert upgrade_planner.mappers == [Mapper(index=1, from_=None, to=None)]

        # Remove missing at index
        with pytest.raises(ValueError):
            upgrade_planner.remove_mapping("transport-belt", "fast-transport-belt", 0)
        assert upgrade_planner.mappers == [Mapper(index=1, from_=None, to=None)]

        # Remove missing at any index
        with pytest.raises(ValueError):
            upgrade_planner.remove_mapping("transport-belt", "fast-transport-belt")
        assert upgrade_planner.mappers == [Mapper(index=1, from_=None, to=None)]

        # Remove first occurence of multiple
        upgrade_planner.set_mapping("inserter", "fast-inserter", 2)
        upgrade_planner.set_mapping("inserter", "fast-inserter", 3)
        upgrade_planner.remove_mapping("inserter", "fast-inserter")
        assert upgrade_planner.mappers == [
            Mapper(index=1, from_=None, to=None),
            Mapper(
                index=3,
                from_={"name": "inserter", "type": "entity"},
                to={"name": "fast-inserter", "type": "entity"},
            ),
        ]

        # Warnings
        # with pytest.warns(ValueWarning):
        #     upgrade_planner.remove_mapping("inserter", "fast-inserter", -1)
        # with pytest.warns(ValueWarning):
        #     upgrade_planner.remove_mapping("inserter", "fast-inserter", 24)

        # Errors
        with pytest.raises(InvalidMapperError):
            upgrade_planner.remove_mapping("inserter", "incorrect")

        with pytest.raises(ValueError):
            upgrade_planner.remove_mapping("inserter", "fast-inserter", "incorrect")

    def test_pop_mapping(self):
        upgrade_planner = UpgradePlanner()

        with draftsman.validators.set_mode(ValidationMode.MINIMUM):
            upgrade_planner.mappers = [
                Mapper(
                    index=1,
                    from_={"name": "express-transport-belt", "type": "entity"},
                    to={"name": "transport-belt", "type": "entity"},
                ),
                Mapper(
                    index=1,
                    from_={"name": "assembling-machine-2", "type": "entity"},
                    to={"name": "assembling-machine-1", "type": "entity"},
                ),
                Mapper(
                    index=0,
                    from_={"name": "fast-transport-belt", "type": "entity"},
                    to={"name": "transport-belt", "type": "entity"},
                ),
            ]

        # Remove mapping with index 0
        upgrade_planner.pop_mapping(0)
        assert upgrade_planner.mappers == [
            Mapper(
                index=1,
                from_={"name": "express-transport-belt", "type": "entity"},
                to={"name": "transport-belt", "type": "entity"},
            ),
            Mapper(
                index=1,
                from_={"name": "assembling-machine-2", "type": "entity"},
                to={"name": "assembling-machine-1", "type": "entity"},
            ),
        ]

        # Remove first mapping with specified index
        upgrade_planner.pop_mapping(1)
        assert upgrade_planner.mappers == [
            Mapper(
                index=1,
                from_={"name": "assembling-machine-2", "type": "entity"},
                to={"name": "assembling-machine-1", "type": "entity"},
            ),
        ]

        # Remove mapping with index not in mappers
        with pytest.raises(ValueError):
            upgrade_planner.pop_mapping(10)
        assert upgrade_planner.mappers == [
            Mapper(
                index=1,
                from_={"name": "assembling-machine-2", "type": "entity"},
                to={"name": "assembling-machine-1", "type": "entity"},
            ),
        ]

    def test_validate(self):
        # We run the suite with `-Werror`, which works great at failing when we
        # make uncaught errors. However, pytest uses `filterwarnings("error")`
        # to achieve this... which causes all warnings that draftsman issues to
        # be treated as exceptions. Under normal circumstances this is fine; but
        # we want warnings to be actaully treated as warnings for this test
        warnings.filterwarnings("default")

        upgrade_planner = UpgradePlanner()

        # Empty should validate
        upgrade_planner.validate().reissue_all()

        # Ensure early-exit is_valid caching works
        # upgrade_planner.validate().reissue_all() # TODO

        # Errors
        with pytest.raises(DataFormatError):
            upgrade_planner.mappers = [{"from": TypeError, "to": TypeError, "index": 1}]

        with pytest.raises(DataFormatError):
            upgrade_planner.mappers = ("incorrect", "incorrect")

        with pytest.raises(DataFormatError):
            upgrade_planner.mappers = [TypeError, TypeError]

        upgrade_planner.mappers = [
            ("assembling-machine-3", None),
            (None, "assembling-machine-3"),
        ]
        assert upgrade_planner.mappers == [
            Mapper(index=0, from_="assembling-machine-3", to=None),
            Mapper(index=1, from_=None, to="assembling-machine-3"),
        ]

        # Test items
        upgrade_planner.mappers = [("speed-module", "speed-module-3")]
        assert upgrade_planner.mappers == [
            Mapper(index=0, from_="speed-module", to="speed-module-3")
        ]

        # Test validation failure
        upgrade_planner = UpgradePlanner()
        with pytest.raises(DataFormatError):
            upgrade_planner.set_mapping("transport-belt", "transport-belt", -1)
        # validation_result = upgrade_planner.validate()
        # assert len(validation_result.error_list) > 0
        # with pytest.raises(DataFormatError):
        #     validation_result.reissue_all()

        # Redundant mapping
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("transport-belt", "transport-belt", 1)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                NoEffectWarning(
                    "Mapping entity/item 'transport-belt' to itself has no effect"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(NoEffectWarning):
            validation_result.reissue_all()

        # Normal upgrade_case
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("transport-belt", "fast-transport-belt", 0)
        goal = ValidationResult(error_list=[], warning_list=[])
        validation_result = upgrade_planner.validate()
        assert validation_result == goal

        # Unrecognized mapping names
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping(
            {"name": "unrecognized-A", "type": "entity"},
            {"name": "unrecognized-B", "type": "entity"},
            0,
        )
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UnknownElementWarning("Unrecognized entity/item 'unrecognized-A'"),
                UnknownElementWarning("Unrecognized entity/item 'unrecognized-B'"),
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UnknownElementWarning):
            validation_result.reissue_all()

        # Known mappers, but mismatch between their types
        upgrade_planner = UpgradePlanner()
        with pytest.warns(UpgradeProhibitedWarning):
            upgrade_planner.mappers = [("speed-module-3", "electric-furnace")]

        # "not-upgradable" flag in from
        upgrade_planner = UpgradePlanner()
        entities.raw["dummy-entity-1"] = {"name": "dummy-entity-1"}
        entities.raw["dummy-entity-1"]["flags"] = {"not-upgradable"}
        upgrade_planner.set_mapping("dummy-entity-1", "fast-transport-belt", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning("'dummy-entity-1' is not upgradable")
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        del entities.raw["dummy-entity-1"]

        # from is not minable
        upgrade_planner = UpgradePlanner()
        entities.raw["dummy-entity-2"] = {"name": "dummy-entity-2"}
        upgrade_planner.set_mapping("dummy-entity-2", "fast-transport-belt", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[UpgradeProhibitedWarning("'dummy-entity-2' is not minable")],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        del entities.raw["dummy-entity-2"]

        # All mining results must not be hidden
        upgrade_planner = UpgradePlanner()
        entities.raw["dummy-entity-3"] = {
            "name": "dummy-entity-3",
            "minable": {"results": [{"name": "hidden-item", "amount": 1}]},
        }
        items.raw["hidden-item"] = {"flags": {"hidden"}}
        upgrade_planner.set_mapping("dummy-entity-3", "fast-transport-belt", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning(
                    "Returned item 'hidden-item' when upgrading 'dummy-entity-3' is hidden"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        del entities.raw["dummy-entity-3"]

        # Cannot upgrade rolling stock
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("cargo-wagon", "fluid-wagon", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning(
                    "Cannot upgrade 'cargo-wagon' because it is RollingStock"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        # Differing collision boxes
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("transport-belt", "electric-furnace", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning(
                    "Cannot upgrade 'transport-belt' to 'electric-furnace'; collision boxes differ"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        # Differing collision masks
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("gate", "stone-wall", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning(
                    "Cannot upgrade 'gate' to 'stone-wall'; collision masks differ"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        # Differing fast replacable group
        upgrade_planner = UpgradePlanner()
        upgrade_planner.set_mapping("radar", "pumpjack", 0)
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                UpgradeProhibitedWarning(
                    "Cannot upgrade 'radar' to 'pumpjack'; fast replacable groups differ"
                )
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(UpgradeProhibitedWarning):
            validation_result.reissue_all()

        # Index outside of meaningful range
        # upgrade_planner = UpgradePlanner()
        # upgrade_planner.set_mapping("fast-transport-belt", "express-transport-belt", 24)
        # goal = ValidationResult(
        #     error_list=[],
        #     warning_list=[
        #         IndexWarning(
        #             "'index' (24) for mapping 'fast-transport-belt' to 'express-transport-belt' must be in range [0, 24) or else it will have no effect"
        #         )
        #     ],
        # )
        # validation_result = upgrade_planner.validate()
        # assert validation_result == goal
        # with pytest.warns(IndexWarning):
        #     validation_result.reissue_all()

        # Multiple mappings sharing the same index
        upgrade_planner = UpgradePlanner()
        with draftsman.validators.set_mode(ValidationMode.MINIMUM):
            upgrade_planner.mappers = [{"index": 0}, {"index": 0}]
        goal = ValidationResult(
            error_list=[],
            warning_list=[
                IndexWarning(
                    "Mapping at index 0 was overwritten 1 time(s); final mapping is 'None' to 'None'"
                ),
            ],
        )
        validation_result = upgrade_planner.validate()
        assert validation_result == goal
        with pytest.warns(IndexWarning):
            validation_result.reissue_all()
