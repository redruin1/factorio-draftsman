# 1KiB_sector_ROM.py

"""
Stores 1024 32-bit signals in a 16x11 tile area (not including encoding or 
decoding), or 4 KiB of data. Can be populated with whatever data you want by 
filling the data array with any set of 32 bit signed integers and a signal 
mapping. The mapping must be large enough to support 256 signals per sector, 
otherwise the encoding will fail. The script will expand to as many needed rows
to fully encapsulate all of the data passed in, in 4KiB increments.

The memory has 2 distinct addresses, allowing it to be read from 2 different
places simultaneously, even in different sectors. These addressing lines are 
denoted 'A' and 'B' respectively. The provided addresser (top-left corner) takes
a single address number and returns the data at that address and at the address
right after it, meaning 'A = input' and 'B = input + 1'.

In order to preserve a full 32 bits while also reserving a bit in order to 
separate desired signals from others, each value is split into a low and high
half, each in the 16-bit range. The result is then recombined in the output to
return the correct 32-bit number. This split is reason why I created this whole
project in the first place, to automate this highly repetitive and error-prone
encoding process.

Technically there is a total data-space of 60 bits available, though utilizing 
this is left as an excercise to the reader, if desired.
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data import signals
from draftsman.entity import (
    ConstantCombinator,
    DeciderCombinator,
    ArithmeticCombinator,
    ElectricPole,
)

import math


class CombinatorCell(Group):
    """
    Regular grid of constant combinators populated with data and linked
    together. Allows the user to set their data in bulk, acting like a single
    combined constant combinator.
    """

    def __init__(
        self,
        id,
        name="combinator-cell",
        position=(0, 0),
        dimension=(1, 1),
        wire_color="red",
        **kwargs
    ):
        # Initialize parent (Group)
        super(CombinatorCell, self).__init__(id, position=position)

        # ID of the cell. Required
        self.id = id

        # Name of the entity. Can be used if you want to specify different types
        # of CombinatorCell with the same class.
        self.name = name
        # Type of the entity. Here we set it to constant-combinator, so that any
        # queries on the blueprint for constant-combinators will also return
        # these objects.
        self._type = "constant-combinator"
        # Name of the constant combinator. Can be substitued with a modded one,
        # but the design would have to change if it was a different dimension.
        combinator_name = "constant-combinator"
        # position (will be the top left corner)
        self.position = position
        # width and height of the grid, from top left to bottom right
        # self._tile_width, self._tile_height = dimension

        self.direction = Direction.NORTH  # Default
        if "direction" in kwargs:  # Optional
            self.direction = kwargs["direction"]

        comb = ConstantCombinator(combinator_name, direction=self.direction)

        # Match the collision mask with the sub-entities
        self._collision_mask = comb.collision_mask

        # number of signal slots per combinator
        self.item_slot_count = comb.item_slot_count

        # Keep a list of combinators in the grid
        for j in range(dimension[1]):
            for i in range(dimension[0]):
                comb.tile_position = ((i * comb.tile_width), (j * comb.tile_height))
                comb.id = str(i) + "_" + str(j)
                self.entities.append(comb)

        # Connect all the combinators to each other
        for j in range(dimension[1]):
            for i in range(dimension[0]):
                current = self.entities[str(i) + "_" + str(j)]
                try:
                    across = self.entities[str(i + 1) + "_" + str(j)]
                    self.add_circuit_connection(wire_color, current.id, across.id)
                except KeyError:
                    pass
                try:
                    below = self.entities[str(i) + "_" + str(j + 1)]
                    self.add_circuit_connection(wire_color, current.id, below.id)
                except KeyError:
                    pass

    def set_data(self, mapping, data):
        """
        Sets the data in the cell. Starts in the top-right combinator, then goes
        across and down, filling each combinator's entry with the signal
        specified by `mapping` and the value specified by `data`.
        """
        assert len(data) <= len(mapping)
        assert len(data) <= self.item_slot_count * self.tile_width * self.tile_height

        for combinator in self.entities:
            combinator.set_signals(None)

        for i, value in enumerate(data):
            current_combinator = self.entities[int(i / self.item_slot_count)]
            # Only set the signal if it's nonzero to save space
            if value:
                current_combinator.set_signal(
                    i % self.item_slot_count, mapping[i], value
                )


def main():
    blueprint = Blueprint()

    # Specify whatever numeric data you would like to encode here.
    # Values can be anything in the signed 32-bit integer range.
    data = [123, 200000000, -10421]

    # Specify the interface signals:
    address_signal = "red-wire"
    sector_index_signal = "green-wire"

    # Blacklist desired signals:
    blacklist = []
    # There are 262 valid vanilla signals in the game
    # We can't use the special signals in constant combinators
    blacklist += ["signal-anything", "signal-everything", "signal-each"]
    # And the interface signals have to be different by nature of this blueprint
    blacklist += [address_signal, sector_index_signal]
    # Which leaves us with 1 spare signal that we can choose to avoid
    # (unless you're using mods)
    blacklist += ["signal-info"]

    assert len(blacklist) <= 6

    # Generate the signal mapping set
    mapping = []

    def add_signals_to_mapping(signals):
        for signal in signals:
            if signal not in blacklist:
                mapping.append(signal)

    add_signals_to_mapping(signals.virtual)
    add_signals_to_mapping(signals.item)
    add_signals_to_mapping(signals.fluid)

    # Sectors are akin to Hard-drive sectors and are where the data is stored
    sector = Group(id="sector_0")

    # Each sector has 4 gates and 4 selectors, 2 for low & high and 2 for A & B
    # Selectors select which the correct signal from the 256 signals from the
    # sector
    selector = DeciderCombinator("decider-combinator")
    selector.set_decider_conditions("signal-each", ">", 2**29, "signal-each")
    selector.copy_count_from_input = True
    selector_ids = [
        "low_selector_a",
        "low_selector_b",
        "high_selector_a",
        "high_selector_b",
    ]
    for i, selector_id in enumerate(selector_ids):
        selector.id = selector_id
        selector.tile_position = (i, 0)
        sector.entities.append(selector)

    # Gates determine which sector the address line is reading from and pass to
    # the selectors
    gate = DeciderCombinator("decider-combinator")
    gate.set_decider_conditions(sector_index_signal, "=", 0, "signal-everything")
    gate.copy_count_from_input = True
    gate_ids = ["low_gate_a", "low_gate_b", "high_gate_a", "high_gate_b"]
    for i, gate_id in enumerate(gate_ids):
        gate.id = gate_id
        gate.tile_position = (i, 2)
        sector.entities.append(gate)

    # Low cell
    cell = CombinatorCell(id="low", dimension=(2, 7))
    cell.position = (0, 4)
    sector.entities.append(cell)

    # High cell
    cell.id = "high"
    cell.position = (2, 4)
    sector.entities.append(cell)

    ### Internal sector connections ###
    # Gate inputs
    sector.add_circuit_connection("red", ("low", "0_0"), "low_gate_a")
    sector.add_circuit_connection("red", "low_gate_a", "low_gate_b")
    sector.add_circuit_connection("red", ("high", "0_0"), "high_gate_a")
    sector.add_circuit_connection("red", "high_gate_a", "high_gate_b")

    sector.add_circuit_connection("green", "low_gate_a", "high_gate_a")
    sector.add_circuit_connection("green", "low_gate_b", "high_gate_b")

    # Selector inputs
    sector.add_circuit_connection("green", "low_gate_a", "low_selector_a", 2, 1)
    sector.add_circuit_connection("green", "low_gate_b", "low_selector_b", 2, 1)
    sector.add_circuit_connection("green", "high_gate_a", "high_selector_a", 2, 1)
    sector.add_circuit_connection("green", "high_gate_b", "high_selector_b", 2, 1)

    sector.add_circuit_connection("red", "low_selector_a", "high_selector_a")
    sector.add_circuit_connection("red", "low_selector_b", "high_selector_b")

    # We generate the blueprint in rows of 4 sectors (4 KiB) and expand as
    # needed
    num_rows = math.ceil((len(data) / 256) / 4)
    num_sectors = num_rows * 4
    for i in range(num_sectors):
        sector.id = "sector_{}".format(i)

        sector_data = data[i * 256 : (i + 1) * 256]
        # Set low bits
        sector.entities["low"].set_data(mapping, [x & 0xFFFF for x in sector_data])
        sector.entities[("low", "1_6")].set_signal(0, sector_index_signal, -i)

        # Set high bits
        sector.entities["high"].set_data(mapping, [x >> 16 for x in sector_data])
        sector.entities[("high", "1_6")].set_signal(0, sector_index_signal, -i)

        # We restrict the width to 4 to fit between substations
        x = i % 4 * sector.tile_width
        y = int(i / 4) * sector.tile_height
        sector.position = (x, y)

        blueprint.entities.append(sector)

    ### Connections between sectors ###
    for y in range(num_rows):
        # Row connections
        for x in range(4):
            i = y * 4 + x
            left_sector = "sector_{}".format(i)
            right_sector = "sector_{}".format(i + 1)

            # fmt: off
            row_connections = [
                # Inputs
                ["green", (left_sector, "high_gate_a"), (right_sector, "low_gate_a")],
                ["green", (left_sector, "high_gate_b"), (right_sector, "low_gate_b")],
                ["red", (left_sector, "high_selector_a"), (right_sector, "low_selector_a")],
                ["red", (left_sector, "high_selector_b"), (right_sector, "low_selector_b")],
                # Outputs
                ["red", (left_sector, "low_selector_a"), (right_sector, "low_selector_a"), 2, 2],
                ["red", (left_sector, "low_selector_b"), (right_sector, "low_selector_b"), 2, 2],
                ["green", (left_sector, "high_selector_a"), (right_sector, "high_selector_a"), 2, 2],
                ["green", (left_sector, "high_selector_b"), (right_sector, "high_selector_b"), 2, 2],
            ]
            # fmt: on

            for connection in row_connections:
                try:
                    blueprint.add_circuit_connection(*connection)
                except KeyError:
                    pass

        # Column connections
        left_above_sector = "sector_{}".format(y * 4)
        left_below_sector = "sector_{}".format((y + 1) * 4)

        right_above_sector = "sector_{}".format(y * 4 + 3)
        right_below_sector = "sector_{}".format((y + 1) * 4 + 3)

        # fmt: off
        column_connections = [
            # Inputs
            ["red", (left_above_sector, "low_selector_a"), (left_below_sector, "low_selector_a")],
            ["red", (left_above_sector, "low_selector_b"), (left_below_sector, "low_selector_b")],
            ["green", (left_above_sector, "low_gate_a"), (left_below_sector, "low_gate_a")],
            ["green", (left_above_sector, "low_gate_b"), (left_below_sector, "low_gate_b")],
            # Ouputs
            ["red", (right_above_sector, "low_selector_a"), (right_below_sector, "low_selector_a"), 2, 2],
            ["red", (right_above_sector, "low_selector_b"), (right_below_sector, "low_selector_b"), 2, 2],
            ["green", (right_above_sector, "high_selector_a"), (right_below_sector, "high_selector_a"), 2, 2],
            ["green", (right_above_sector, "high_selector_b"), (right_below_sector, "high_selector_b"), 2, 2],
        ]
        # fmt: on

        for connection in column_connections:
            try:
                blueprint.add_circuit_connection(*connection)
            except KeyError:
                pass

    # =========================================================================
    ### Signal addressing/encoding ###

    mapping_cell = CombinatorCell(
        id="mapping", direction=Direction.SOUTH, dimension=(7, 2), position=(5, -2)
    )
    mapping_cell.set_data(mapping, range(1, 257))
    mapping_cell.entities["6_1"].set_signal(0, address_signal, 1)
    blueprint.entities.append(mapping_cell)

    adjustment = ConstantCombinator(direction=Direction.WEST)

    adjustment.id = "b_offset"
    adjustment.tile_position = (4, -2)
    adjustment.set_signal(0, address_signal, 1)
    blueprint.entities.append(adjustment)

    adjustment.id = "norm_offset"
    adjustment.tile_position = (4, -1)
    adjustment.set_signal(0, address_signal, 2)
    blueprint.entities.append(adjustment)

    address_input = ConstantCombinator(direction=Direction.SOUTH)
    address_input.id = "address_input"
    address_input.tile_position = (0, -7)
    address_input.set_signal(0, address_signal, 1)
    blueprint.entities.append(address_input)

    signal_modulus = ArithmeticCombinator(direction=Direction.SOUTH)
    signal_modulus.set_arithmetic_conditions(address_signal, "%", 256, address_signal)

    signal_modulus.id = "signal_modulus_a"
    signal_modulus.tile_position = (0, -5)
    blueprint.entities.append(signal_modulus)

    signal_modulus.id = "signal_modulus_b"
    signal_modulus.tile_position = (2, -5)
    blueprint.entities.append(signal_modulus)

    sector_selector = ArithmeticCombinator(direction=Direction.SOUTH)
    sector_selector.set_arithmetic_conditions(
        address_signal, "/", 256, sector_index_signal
    )

    sector_selector.id = "sector_selector_a"
    sector_selector.tile_position = (1, -5)
    blueprint.entities.append(sector_selector)

    sector_selector.id = "sector_selector_b"
    sector_selector.tile_position = (3, -5)
    blueprint.entities.append(sector_selector)

    signal_selector = DeciderCombinator(direction=Direction.SOUTH)
    signal_selector.set_decider_conditions(
        "signal-each", "=", address_signal, "signal-each"
    )
    signal_selector.copy_count_from_input = False

    signal_selector.id = "signal_selector_a"
    signal_selector.tile_position = (0, -3)
    blueprint.entities.append(signal_selector)

    signal_selector.id = "signal_selector_b"
    signal_selector.tile_position = (2, -3)
    blueprint.entities.append(signal_selector)

    signal_normalizer = ArithmeticCombinator(direction=Direction.SOUTH)
    signal_normalizer.set_arithmetic_conditions(-1, "%", address_signal, address_signal)

    signal_normalizer.id = "signal_norm_a"
    signal_normalizer.tile_position = (1, -3)
    blueprint.entities.append(signal_normalizer)

    signal_normalizer.id = "signal_norm_b"
    signal_normalizer.tile_position = (3, -3)
    blueprint.entities.append(signal_normalizer)

    shifter = ArithmeticCombinator(direction=Direction.WEST)
    shifter.set_arithmetic_conditions("signal-each", "<<", 30, "signal-each")

    shifter.id = "shifter_a"
    shifter.tile_position = (0, -1)
    blueprint.entities.append(shifter)

    shifter.tile_position = (2, -1)
    shifter.id = "shifter_b"
    blueprint.entities.append(shifter)

    in_connections = [
        ["red", "address_input", "signal_modulus_a"],
        ["red", "signal_modulus_a", "sector_selector_a"],
        ["red", "sector_selector_a", "signal_modulus_b"],
        ["red", "signal_modulus_b", "sector_selector_b"],
        ["green", "sector_selector_a", ("sector_0", "low_gate_a"), 2, 1],
        ["green", "sector_selector_b", ("sector_0", "low_gate_b"), 2, 1],
        ["green", "signal_modulus_a", "signal_selector_a", 2, 1],
        ["green", "signal_selector_a", "signal_norm_a"],
        ["green", "signal_modulus_b", "signal_selector_b", 2, 1],
        ["green", "signal_selector_b", "signal_norm_b"],
        ["red", "signal_selector_b", ("mapping", "0_0")],
        ["red", "signal_selector_a", "signal_selector_b"],
        ["green", "b_offset", "sector_selector_b"],
        ["green", "sector_selector_b", "signal_modulus_b"],
        ["red", "norm_offset", "signal_norm_b"],
        ["red", "signal_norm_b", "signal_norm_a"],
        ["red", "signal_selector_a", "signal_norm_a", 2, 2],
        ["red", "signal_norm_a", "shifter_a", 2, 1],
        ["red", "signal_selector_b", "signal_norm_b", 2, 2],
        ["red", "signal_norm_b", "shifter_b", 2, 1],
        ["red", "shifter_a", ("sector_0", "low_selector_a"), 2, 1],
        ["red", "shifter_b", ("sector_0", "low_selector_b"), 2, 1],
    ]

    for connection in in_connections:
        blueprint.add_circuit_connection(*connection)

    # =========================================================================
    ### Signal output/decoding ###

    output_decoder = ArithmeticCombinator("arithmetic-combinator")

    output_decoder.id = "low_out_a"
    output_decoder.tile_position = (12, -2)
    output_decoder.set_arithmetic_conditions("signal-each", "AND", 0xFFFF, "signal-A")
    blueprint.entities.append(output_decoder)

    output_decoder.id = "low_out_b"
    output_decoder.tile_position = (13, -2)
    output_decoder.set_arithmetic_conditions("signal-each", "AND", 0xFFFF, "signal-B")
    blueprint.entities.append(output_decoder)

    output_decoder.id = "high_out_a"
    output_decoder.tile_position = (14, -2)
    output_decoder.set_arithmetic_conditions("signal-each", "<<", 16, "signal-A")
    blueprint.entities.append(output_decoder)

    output_decoder.id = "high_out_b"
    output_decoder.tile_position = (15, -2)
    output_decoder.set_arithmetic_conditions("signal-each", "<<", 16, "signal-B")
    blueprint.entities.append(output_decoder)

    pole = ElectricPole("medium-electric-pole")

    pole.id = "out_a"
    pole.tile_position = (12, -7)
    blueprint.entities.append(pole)

    pole.id = "out_b"
    pole.tile_position = (15, -7)
    blueprint.entities.append(pole)

    out_connections = [
        ["red", ("sector_3", "low_selector_a"), "low_out_a", 2, 1],
        ["red", ("sector_3", "low_selector_b"), "low_out_b", 2, 1],
        ["green", ("sector_3", "high_selector_a"), "high_out_a", 2, 1],
        ["green", ("sector_3", "high_selector_b"), "high_out_b", 2, 1],
        ["red", "low_out_a", "high_out_a", 2, 2],
        ["red", "low_out_a", "out_a", 2, 1],
        ["red", "low_out_b", "high_out_b", 2, 2],
        ["red", "low_out_b", "out_b", 2, 1],
    ]

    for connection in out_connections:
        blueprint.add_circuit_connection(*connection)

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
