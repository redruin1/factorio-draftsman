# seisras.py

"""
Creates a bunch of components for the SEISRAS CPU.
"""

from draftsman.blueprintable import Blueprint, Group
from draftsman.constants import Direction, ValidationMode
from draftsman.entity import ConstantCombinator, DeciderCombinator, DisplayPanel
from draftsman.signatures import SignalID, SignalFilter
import draftsman.validators

from draftsman.data import signals

from examples.decider_bit_checker import determine_bit_conditions

import pyperclip

import string


INSTR_ADDRESS_0 = SignalID("cut-paste-tool", "item", "normal")
INSTR_ADDRESS_1 = SignalID("cut-paste-tool", "item", "uncommon")
INSTR_ADDRESS_2 = SignalID("cut-paste-tool", "item", "rare")
INSTR_ADDRESS_3 = SignalID("cut-paste-tool", "item", "epic")
WRITEBACK_ADDRESS = SignalID("cut-paste-tool", "item", "legendary")
INSTR_OUTPUT_0 = SignalID("copy-paste-tool", "item", "normal")
INSTR_OUTPUT_1 = SignalID("copy-paste-tool", "item", "uncommon")
INSTR_OUTPUT_2 = SignalID("copy-paste-tool", "item", "rare")
INSTR_OUTPUT_3 = SignalID("copy-paste-tool", "item", "epic")
INSTR_OUTPUT_3 = SignalID("copy-paste-tool", "item", "epic")
CPU_RESET_SIGNAL = SignalID("copy-paste-tool", "item", "legendary")


def main():
    draftsman.validators.set_mode(ValidationMode.DISABLED)

    # We prohibit these signals in the indexing array
    BLACKLISTED_INDEX_SIGNALS = [
        ("cut-paste-tool", "item", "normal"),
        ("cut-paste-tool", "item", "uncommon"),
        ("cut-paste-tool", "item", "rare"),
        ("cut-paste-tool", "item", "epic"),
        ("cut-paste-tool", "item", "legendary"),
        ("copy-paste-tool", "item", "normal"),
        ("copy-paste-tool", "item", "uncommon"),
        ("copy-paste-tool", "item", "rare"),
        ("copy-paste-tool", "item", "epic"),
        ("copy-paste-tool", "item", "legendary"),
    ]
    # Each sector gets an icon signal with a display panel for ease of
    # identification. We start with numerics, and then switch to the alphabet;
    # anything more than 36 sectors is kinda insane
    SECTOR_LABELS = [
        "signal-{}".format(char) for char in string.digits + string.ascii_uppercase
    ]

    # A list of all possible signal names
    all_signals = (
        signals.virtual
        + signals.item
        + signals.recipe
        + signals.fluid
        + signals.space_location
        + signals.entity
        + signals.quality
    )

    # Idiot check: ensure that the signals that we've blacklisted are real signals
    for index_signal in BLACKLISTED_INDEX_SIGNALS:
        assert index_signal[0] in all_signals, index_signal

    # Collate all signals, ignoring quality
    base_signals = []
    for signal_name in all_signals:
        if (
            signal_name in signals.pure_virtual
        ):  # wildcards cannot exist in constant combinators
            continue
        if "parameter" in signal_name:  # parameters are not discernable signals
            continue
        if (
            signal_name == "signal-unknown"
        ):  # cannot be discerned (all other unknowns are fine though)
            continue
        for signal_type in signals.type_of[signal_name]:
            base_signals.append((signal_name, signal_type))

    # Create the master indexing list, specifying all normal quality signals
    # first, followed by uncommon signals, then rare, etc.
    index_signals = []  # The master indexing list
    used_signals = set()
    for signal_quality in signals.quality:
        for signal_name, signal_type in base_signals:
            index_signal = (signal_name, signal_type, signal_quality)

            if (
                index_signal in BLACKLISTED_INDEX_SIGNALS
                or index_signal in used_signals
            ):
                continue

            index_signals.append(index_signal)
            used_signals.add(index_signal)

    print("Index list size:", len(index_signals))

    # The set of raw data that should stored into RAM
    compiled_data = [0xFF, 0xFF, 0xFF, 0xFF]

    # Create a blueprint to hold the RAM
    RAM_blueprint = Blueprint(label="RAM")

    # Dump a (single) constant combinator which contains the indexing constants
    index_cc = ConstantCombinator(direction=Direction.SOUTH, tile_position=(0, -3))
    signal_index = 0
    section_index = 0
    signal_count = 0
    for signal_name, signal_type, signal_quality in index_signals:
        if signal_index == 0:
            index_cc.add_section()  # "Index ({})".format(section_index)
            current_section = index_cc.sections[-1]

        current_section.set_signal(
            index=signal_index,
            name=signal_name,
            count=signal_count + 1,
            type=signal_type,
            quality=signal_quality,
        )
        signal_index += 1
        signal_count += 1

        if signal_index == 1000:
            signal_index = 0
            section_index += 1

    RAM_blueprint.entities.append(index_cc)

    # Create a (single) constant combinator which selects which signal from the
    # ALU depending on the opcode's value
    ALU_opcode_table = ConstantCombinator(
        id="ALU_opcode_table",
        direction=Direction.SOUTH,
        tile_position=(1, -3),
        player_description="ALU_opcode_table",
    )
    section = ALU_opcode_table.add_section()
    section.filters = [
        # TODO
    ]
    RAM_blueprint.entities.append(ALU_opcode_table)

    # Build the RAM sector
    RAM_sector = Group()

    # Add a display panel to give a label to the sector
    display_panel = DisplayPanel(
        id="display_panel",
        direction=Direction.SOUTH,
        tile_position=(-1, 1),
        player_description="sector label",
    )
    RAM_sector.entities.append(display_panel)

    # Create the multiplexer, which outputs the selected value from the ALU per
    # the given opcode, but across every single indexing signal
    # Due to wire shenanegans, we need to have one of these per sector
    ALU_multiplexer = DeciderCombinator(
        id="ALU_multiplexer",
        direction=Direction.SOUTH,
        tile_position=(0, 0),
        player_description="ALU_multiplexer",
    )
    ALU_multiplexer.conditions = [
        DeciderCombinator.Condition(
            first_signal="signal-each",
            first_signal_networks={"green"},
            comparator="=",
            second_signal="signal-info",
            second_signal_networks={"green"},
        )
    ]
    ALU_multiplexer.outputs = [
        DeciderCombinator.Output(signal=SignalID(*sig), networks={"red"})
        for sig in index_signals
    ]
    RAM_sector.entities.append(ALU_multiplexer)

    # Select only the signal that matches the given indexing table (offset by
    # the constant sector address shift)
    write_filter = DeciderCombinator(
        id="write_filter",
        direction=Direction.SOUTH,
        tile_position=(1, 0),
        player_description="write_filter",
    )
    write_filter.conditions = DeciderCombinator.Condition(
        first_signal="signal-each",
        first_signal_networks={"red"},
        comparator="=",
        second_signal=WRITEBACK_ADDRESS,
    ) | DeciderCombinator.Condition(
        first_signal=WRITEBACK_ADDRESS,
        first_signal_networks={"green"},
        comparator="!=",
        constant=0,
    ) & DeciderCombinator.Condition(
        first_signal="signal-each",
        first_signal_networks={"green"},
        comparator="=",
        second_signal=WRITEBACK_ADDRESS,
    )
    write_filter.outputs = [
        DeciderCombinator.Output(signal="signal-each", networks={"green"})
    ]
    RAM_sector.entities.append(write_filter)
    RAM_sector.add_circuit_connection(
        "green", "ALU_multiplexer", "write_filter", "output", "input"
    )

    # Constant combinator which holds the sector offset
    sector_offset_cc = ConstantCombinator(
        id="sector_offset_cc",
        direction=Direction.WEST,
        tile_position=(2, 0),
    )
    sector_offset_cc.add_section().set_signal
    RAM_sector.entities.append(sector_offset_cc)
    RAM_sector.add_circuit_connection("green", "sector_offset_cc", "write_filter")

    # Actual memory cell
    memory_cell = DeciderCombinator(
        id="memory_cell", direction=Direction.EAST, tile_position=(2, 1)
    )
    memory_cell.conditions = DeciderCombinator.Condition(
        first_signal=CPU_RESET_SIGNAL, comparator="=", constant=0
    ) & DeciderCombinator.Condition(
        first_signal="signal-each",
        first_signal_networks={"red"},
        comparator="!=",
        second_signal=WRITEBACK_ADDRESS,
    )
    memory_cell.outputs = [
        DeciderCombinator.Output(signal="signal-each", networks={"green"})
    ]
    RAM_sector.entities.append(memory_cell)
    RAM_sector.add_circuit_connection("red", "write_filter", "memory_cell")
    RAM_sector.add_circuit_connection(
        "green", "write_filter", "memory_cell", "output", "input"
    )
    RAM_sector.add_circuit_connection(
        "green", "memory_cell", "memory_cell", "input", "output"
    )

    # Create the ROM combinator which actually holds the encoded data for this sector
    ROM_cc = ConstantCombinator(
        id="ROM_cc",
        direction=Direction.EAST,
        tile_position=(3, 0),
        player_description="ROM_cc",
    )
    ROM_cc.add_section()
    RAM_sector.entities.append(ROM_cc)

    # Create the reset gate for the ROM combinator
    reset_gate = DeciderCombinator(
        id="reset_gate",
        direction=Direction.SOUTH,
        tile_position=(4, 0),
        player_description="reset_gate",
    )
    reset_gate.conditions = [
        DeciderCombinator.Condition(
            first_signal=CPU_RESET_SIGNAL,
            first_signal_networks={"red"},
            comparator="!=",
            constant=0,
        )
    ]
    reset_gate.outputs = [
        DeciderCombinator.Output(
            signal="signal-everything",
            networks={"green"},
        )
    ]
    RAM_sector.entities.append(reset_gate)
    RAM_sector.add_circuit_connection("green", "ROM_cc", "reset_gate")
    RAM_sector.add_circuit_connection("red", "memory_cell", "reset_gate")
    RAM_sector.add_circuit_connection(
        "green", "memory_cell", "reset_gate", "output", "output"
    )

    # Add 4 instruction address readers
    inputs = [INSTR_ADDRESS_0, INSTR_ADDRESS_1, INSTR_ADDRESS_2, INSTR_ADDRESS_3]
    outputs = [INSTR_OUTPUT_0, INSTR_OUTPUT_1, INSTR_OUTPUT_2, INSTR_OUTPUT_3]
    read_decider = DeciderCombinator(
        direction=Direction.NORTH,
    )
    for count, input_signal, output_signal in zip(range(4), inputs, outputs):
        read_decider.id = "read_decider_{}".format(count)
        read_decider.tile_position = (count + 5, 0)
        read_decider.conditions = []
        for sector_i, index_signal in enumerate(index_signals):
            read_decider.conditions += DeciderCombinator.Condition(
                first_signal=input_signal,
                first_signal_networks={"red"},
                comparator="=",
                constant=sector_i + 1,
            ) & DeciderCombinator.Condition(
                first_signal="signal-each",
                first_signal_networks={"red"},
                comparator="=",
                second_signal=SignalID(*index_signal),
                second_signal_networks={"red"},
            )
        read_decider.outputs = [
            DeciderCombinator.Output(signal=output_signal, networks={"green"})
        ]
        RAM_sector.entities.append(read_decider)

    # Wire the address readers
    connections = [
        ("red", "reset_gate", "read_decider_0", "input", "output"),
        ("red", "read_decider_0", "read_decider_1", "output", "output"),
        ("red", "read_decider_1", "read_decider_2", "output", "output"),
        ("red", "read_decider_2", "read_decider_3", "output", "output"),
        ("red", "read_decider_0", "read_decider_0", "input", "output"),
        ("red", "read_decider_0", "read_decider_1", "input", "input"),
        ("red", "read_decider_1", "read_decider_2", "input", "input"),
        ("red", "read_decider_2", "read_decider_3", "input", "input"),
        # Green inputs
        ("green", "reset_gate", "read_decider_0", "output", "input"),
        ("green", "read_decider_0", "read_decider_1", "input", "input"),
        ("green", "read_decider_1", "read_decider_2", "input", "input"),
        ("green", "read_decider_2", "read_decider_3", "input", "input"),
        # Green outputs
        ("green", "read_decider_0", "read_decider_1", "output", "output"),
        ("green", "read_decider_1", "read_decider_2", "output", "output"),
        ("green", "read_decider_2", "read_decider_3", "output", "output"),
    ]
    for connection in connections:
        RAM_sector.add_circuit_connection(*connection)

    # Create the 3 indirection combinators
    indirected_signals = [INSTR_OUTPUT_1, INSTR_OUTPUT_2, INSTR_OUTPUT_3]
    for count, indirected_signal in zip(range(4), indirected_signals):
        read_decider.id = "indirection_{}".format(count)
        read_decider.tile_position = (count + 9, 0)
        read_decider.conditions = determine_bit_conditions(
            bit_number=count,
            on=True,
            signal=INSTR_OUTPUT_0,
            additional_condition=DeciderCombinator.Condition(
                first_signal="signal-each",
                first_signal_networks={"red"},
                comparator="=",
                second_signal=indirected_signal,
                second_signal_networks={"red"},
            ),
        )
        read_decider.outputs = [
            DeciderCombinator.Output(signal=indirected_signal, networks={"green"})
        ]
        RAM_sector.entities.append(read_decider)

    # Wire the indirection combinators
    connections = [
        # Red Inputs
        ("red", "read_decider_3", "indirection_0", "input", "input"),
        ("red", "indirection_0", "indirection_1", "input", "input"),
        ("red", "indirection_1", "indirection_2", "input", "input"),
        # Green inputs
        ("green", "read_decider_3", "indirection_0", "input", "input"),
        ("green", "indirection_0", "indirection_1", "input", "input"),
        ("green", "indirection_1", "indirection_2", "input", "input"),
        # Red outputs
        ("red", "indirection_0", "indirection_1", "output", "output"),
        ("red", "indirection_1", "indirection_2", "output", "output"),
    ]
    for connection in connections:
        RAM_sector.add_circuit_connection(*connection)

    # Now actually add the architected sector to the actual blueprint, adding
    # multiple copies as needed to store the entire contents of `compiled_data`
    num_sectors = 2  # math.ceil(len(compiled_data) / len(index_signals))
    for sector_i in range(num_sectors):
        # Display Panel icon
        RAM_sector.entities["display_panel"].icon = SECTOR_LABELS[sector_i]
        # Sector offset
        RAM_sector.entities["sector_offset_cc"].sections[-1].set_signal(
            index=0,
            name="cut-paste-tool",
            quality="legendary",
            count=-len(index_signals) * sector_i,
        )
        # ROM
        data_range_start = sector_i * len(index_signals)
        data_range_end = (sector_i + 1) * len(index_signals)
        RAM_sector.entities["ROM_cc"].sections[-1].filters = [
            SignalFilter(
                index=data_i + 1,
                name=index_signals[data_i][0],
                type=index_signals[data_i][1],
                quality=index_signals[data_i][2],
                count=data,
            )
            for data_i, data in enumerate(
                compiled_data[data_range_start:data_range_end]
            )
        ]
        # Sector position
        RAM_sector.position = (0, sector_i * 2)
        # Add sector with unique ID
        RAM_blueprint.entities.append(RAM_sector, id="sector_{}".format(sector_i))

        # Wire the sector to the previous one (if creating multiple)
        if sector_i != 0:
            RAM_blueprint.add_circuit_connection(
                "red",
                ("sector_{}".format(sector_i - 1), "ALU_multiplexer"),
                ("sector_{}".format(sector_i), "ALU_multiplexer"),
                "input",
                "input",
            )
            RAM_blueprint.add_circuit_connection(
                "green",
                ("sector_{}".format(sector_i - 1), "ALU_multiplexer"),
                ("sector_{}".format(sector_i), "ALU_multiplexer"),
                "input",
                "input",
            )
            RAM_blueprint.add_circuit_connection(
                "red",
                ("sector_{}".format(sector_i - 1), "write_filter"),
                ("sector_{}".format(sector_i), "write_filter"),
                "input",
                "input",
            )
            RAM_blueprint.add_circuit_connection(
                "green",
                ("sector_{}".format(sector_i - 1), "read_decider_3"),
                ("sector_{}".format(sector_i), "read_decider_3"),
                "output",
                "output",
            )
            RAM_blueprint.add_circuit_connection(
                "red",
                ("sector_{}".format(sector_i - 1), "indirection_2"),
                ("sector_{}".format(sector_i), "indirection_2"),
                "output",
                "output",
            )

    pyperclip.copy(RAM_blueprint.to_string())


if __name__ == "__main__":
    main()
