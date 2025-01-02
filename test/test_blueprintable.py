# test_blueprintable.py

from draftsman.blueprintable import *
from draftsman.error import (
    DataFormatError,
    MalformedBlueprintStringError,
    IncorrectBlueprintTypeError,
)
from draftsman.utils import JSON_to_string

import pytest


class TestBlueprintable:
    def test_init(self):
        with pytest.raises(DataFormatError):
            blueprint = Blueprint(["incorrect", "data"])

    def test_load_from_string(self):
        with pytest.raises(IncorrectBlueprintTypeError):
            # Pass a BlueprintBook string into a Blueprint object
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )

    def test_item(self):
        blueprint = Blueprint()
        assert blueprint.item == "blueprint"

        decon_planner = DeconstructionPlanner()
        assert decon_planner.item == "deconstruction-planner"

        upgrade_planner = UpgradePlanner()
        assert upgrade_planner.item == "upgrade-planner"

        blueprint_book = BlueprintBook()
        assert blueprint_book.item == "blueprint-book"

    # def test_formatted_label(self): # TODO
    #     blueprint = Blueprint()

    #     # None case
    #     assert blueprint.formatted_label() == None

    #     pass


class TestBlueprintUtils:
    def test_get_blueprintable_from_string(self):
        # Valid Format (Blueprint)
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        assert isinstance(blueprintable, Blueprint)

        # Valid Format (DeconstructionPlanner)
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkpJTc7PKy4pKk0uyczPiy/ISczLSy1SsqpWKk4tKcnMSy9WssorzcnRUcosSc1VskLToAvToKNUllpUDBRRsjKyMDQxtzQyNzUDIhOL2loAsN4j2w=="
        )
        assert isinstance(blueprintable, DeconstructionPlanner)

        # Valid Format (UpgradePlanner)
        blueprintable = get_blueprintable_from_string(
            "0eNqrViotSC9KTEmNL8hJzMtLLVKyqlYqTi0pycxLL1ayyivNydFRyixJzVWygqnUhanUUSpLLSrOzM9TsjKyMDQxtzQyNzUDIhOL2loAhpkdww=="
        )
        assert isinstance(blueprintable, UpgradePlanner)

        # Valid format (BlueprintBook)
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        )
        assert isinstance(blueprintable, BlueprintBook)

        # Test description key
        blueprintable = get_blueprintable_from_string(
            "0eNrNlNtugzAMht/F16Eqh4TDq1RVxcFl0SCgBNqxinefCxtdByrrXRFChNjf79jGF0iKFmstVQPRBWRaKQPR7gJG5iourt9UXCJEkGBMm9AzkCrDD4jsfs8AVSMbiaPPsOgOqi0T1GTAfnyxwLTRMrVQoc47i9RQH+MUgUFdGSIQmaSI6oqAQUfObkhSSXs8oj4Y+UkYeztdPZupOZNaInNrUqyrYlHFH1U8u19guU+x/Ics7ylWED5icfanGnMA5xv+jXA3fAki/gEJ7iBU8gbLscYy+9UTpkbMrLLK2gItF26GZKcOUp1IutLd6HhbUWOYJk7fIRoKubhD3dXTPQ/fXw9fiLUcBOsQX7xuDsL18IMXLqG9neKPjcEyKaTKrTJO36S6BjE/TWjfV5Qmz1nqYezsHMaZy/ie7ejJPHrbj4e4pmcabgxOqM2A5MIJvTDk3OHCdehH+wIapKEo"
        )
        assert blueprintable.to_dict() == {
            "blueprint": {
                "icons": [{"signal": {"name": "beacon"}, "index": 1}],
                "entities": [
                    {
                        "entity_number": 1,
                        "name": "electric-energy-interface",
                        "position": {"x": 368, "y": 139},
                        # "buffer_size": 10000000000 # Default
                    },
                    {
                        "entity_number": 2,
                        "name": "big-electric-pole",
                        "position": {"x": 367, "y": 141},
                    },
                    {
                        "entity_number": 3,
                        "name": "big-electric-pole",
                        "position": {"x": 377, "y": 141},
                    },
                    {
                        "entity_number": 4,
                        "name": "big-electric-pole",
                        "position": {"x": 389, "y": 141},
                    },
                    {
                        "entity_number": 5,
                        "name": "beacon",
                        "position": {"x": 355.5, "y": 143.5},
                    },
                    {
                        "entity_number": 6,
                        "name": "beacon",
                        "position": {"x": 358.5, "y": 143.5},
                        "items": [
                            {
                                "id": {"name": "speed-module-3"},
                                "items": {
                                    "in_inventory": [
                                        {"inventory": 1, "stack": 0},
                                        {"inventory": 1, "stack": 1},
                                    ]
                                },
                            }
                        ],
                    },
                    {
                        "entity_number": 7,
                        "name": "beacon",
                        "position": {"x": 366.5, "y": 143.5},
                    },
                    {
                        "entity_number": 8,
                        "name": "beacon",
                        "position": {"x": 376.5, "y": 143.5},
                        "items": [
                            {
                                "id": {"name": "speed-module-3"},
                                "items": {
                                    "in_inventory": [
                                        {"inventory": 1, "stack": 0},
                                        {"inventory": 1, "stack": 1},
                                    ]
                                },
                            }
                        ],
                    },
                    {
                        "entity_number": 9,
                        "name": "beacon",
                        "position": {"x": 388.5, "y": 143.5},
                        "items": [
                            {
                                "id": {"name": "speed-module-3"},
                                "items": {
                                    "in_inventory": [
                                        {"inventory": 1, "stack": 0},
                                        {"inventory": 1, "stack": 1},
                                    ]
                                },
                            }
                        ],
                    },
                    {
                        "entity_number": 10,
                        "name": "assembling-machine-3",
                        "position": {"x": 391.5, "y": 143.5},
                    },
                ],
                "wires": [[2, 5, 3, 5], [3, 5, 4, 5]],
                "item": "blueprint",
                "version": 562949955256321,
            }
        }

        # Invalid format
        with pytest.raises(MalformedBlueprintStringError):
            get_blueprintable_from_string("0lmaothisiswrong")

        example = JSON_to_string({"incorrect": {}})
        with pytest.raises(IncorrectBlueprintTypeError):
            get_blueprintable_from_string(example)

    def test_get_blueprintable_from_JSON(self):
        # Valid Format (Blueprint)
        json_dict = {"blueprint": {"item": "blueprint"}}
        blueprintable = get_blueprintable_from_JSON(json_dict)
        assert isinstance(blueprintable, Blueprint)

        # Valid Format (DeconstructionPlanner)
        json_dict = {"deconstruction_planner": {"item": "deconstruction-planner"}}
        blueprintable = get_blueprintable_from_JSON(json_dict)
        assert isinstance(blueprintable, DeconstructionPlanner)

        # Valid Format (UpgradePlanner)
        json_dict = {"upgrade_planner": {"item": "upgrade-planner"}}
        blueprintable = get_blueprintable_from_JSON(json_dict)
        assert isinstance(blueprintable, UpgradePlanner)

        # Valid format (BlueprintBook)
        json_dict = {"blueprint_book": {"item": "blueprint-book"}}
        blueprintable = get_blueprintable_from_JSON(json_dict)
        assert isinstance(blueprintable, BlueprintBook)

        example = {"incorrect": {}}
        with pytest.raises(IncorrectBlueprintTypeError):
            get_blueprintable_from_JSON(example)
