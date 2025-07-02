# train_configuration.py

from draftsman.entity import new_entity

from math import ceil
from typing import Literal
import re


_digit_regex = re.compile("((\\d+)([^\\d]))|((\\d+)())|(()([^\\d]))")


class TrainConfiguration:
    """
    A utility object which holds a set of connected rolling stock in a
    particular order and configuration.
    """

    # The default kwargs that correspond to each of the string format characters
    default_mapping = {
        "<": {"name": "locomotive"},
        ">": {"name": "locomotive", "orientation": 0.5},
        "C": {"name": "cargo-wagon"},
        "F": {"name": "fluid-wagon"},
        "A": {"name": "artillery-wagon"},
    }

    def __init__(
        self,
        format_string: str = None,
        direction: Literal["dual", "forward"] = "dual",
        wagons: Literal["cargo", "fluid", "artillery"] = "cargo",
        mapping: dict[str, dict] = default_mapping,
    ) -> None:
        if format_string is None:
            self.cars: list[RollingStock] = []
        else:
            self.from_string(
                format_string, direction=direction, wagons=wagons, mapping=mapping
            )

    # =========================================================================

    @property
    def rail_length(self) -> int:
        """
        Returns the minimum amount of straight rail pieces needed to fully place
        this configuration in a straight line. Read only.
        """
        return ceil((len(self.cars) * 7) / 2)

    # =========================================================================

    def from_string(
        self,
        format_string: str = None,
        direction: Literal["dual", "forward"] = "dual",
        wagons: Literal["cargo", "fluid", "artillery"] = "cargo",
        mapping: dict[str, dict] = default_mapping,
    ) -> None:
        """
        Create a list of valid connected rolling stock via a user-friendly
        format string.

        TODO: example

        :param format_string: The input string to interpret. Must contain only
            the uppercase characters, as defined in ``mapping``.
        :param direction: Whether or not this train should define all of it's
            locomotives facing the same direction (``forward``) or facing
            opposite directions at each end (``dual``) if the notation is left
            ambiguous. Dual format only works if there are only two locomotive
            groups total.
        :param wagons: What kind of cargo wagon should be inserted inbetween
            locomotive groups if the notation is left ambiguous.
        :param mapping: A dictionary mapping individual characters found in the
            format strings to a dictionary of kwargs that get passed to
            :py:func:`.new_entity`. For an example, see
            :py:attr:`TrainConfiguration.default_mapping`.
        """
        # Normalize input
        format_string = format_string.upper()
        direction = direction.lower()
        wagons = wagons.lower()

        if direction not in {"dual", "forward"}:
            raise ValueError("Argument 'direction' must be one of 'dual' or 'forward'")

        if wagons not in {"cargo", "fluid", "artillery"}:
            raise ValueError(
                "Argument 'wagons' must be one of 'cargo', 'fluid', or 'artillery'"
            )

        # Convert user-readable to explicit format
        wagon_symbols = {"cargo": "C", "fluid": "F", "artillery": "A"}
        wagons = wagon_symbols[wagons]

        # Split the string by hyphens '-'
        # Hyphens indicate when the current_default_type should change from
        # locomotives to wagons and back
        hyphen_blocks = format_string.split("-")

        # Check to see if we have a special dual-headed train
        if (
            len(hyphen_blocks) == 3 and direction == "dual"
        ):  # Special x-y-x dual-headed format
            dual_headed = True
        else:
            # Otherwise all locomotive blocks point forward
            dual_headed = False

        # Converts the string into the explicit format where each character
        # corresponds to one car
        # e.g. "2-2C2F4A-2" into "<<CCFFAAAA>>"
        result_string = ""
        for i, hyphen_block in enumerate(hyphen_blocks):
            if dual_headed and i == 2:
                current_default_type = ">"
            elif i % 2 == 0:
                current_default_type = "<"
            else:
                current_default_type = wagons
            # Regex iterate over the text matching "(digits)([<>CFA])"
            for match in re.finditer(_digit_regex, hyphen_block):
                if match.group(1):
                    amt = match.group(2) or 1
                    car = match.group(3) or current_default_type
                if match.group(4):
                    amt = match.group(5) or 1
                    car = match.group(6) or current_default_type
                if match.group(7):
                    amt = match.group(8) or 1
                    car = match.group(9) or current_default_type

                if car not in mapping:
                    raise ValueError(
                        "Encountered unexpected character '{}'\n"
                        "\t{}\n"
                        "\t{}".format(car, format_string, " " * i + "^")
                    )

                # Construct a new string
                replacement = car * int(amt)

                result_string += replacement

        # Iterate over the explicit string and add a wagon of each type per char
        self.cars = []
        for i, char in enumerate(result_string):
            self.cars.append(new_entity(**mapping[char]))
