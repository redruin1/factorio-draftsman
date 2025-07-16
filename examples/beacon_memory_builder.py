# beacon_memory_builder.py

"""
Constructs a blueprint of a variable-size addressable RAM module, wherin the
data stored is with modules stored in beacons. While not very information dense,
this has the unique property that encoded information is not lost when copied
or destroyed; you could drop a nuke on this memory cell and would retain all of
it's information once rebuilt. In this sense, this memory cell behaves almost
akin to a hard-drive, which can be copied to a blueprint string and shared
between computers or save-games.

5 input signals control it's behavior, interfaced on the bottom left corner of
the blueprint:

* `S`, the size of data to read in bytes. Can be one of `1`, `2`, `4`; other
    values produce no result.
* `A`, the address to read from, 0-based. Must be a multiple of `S`, or else
    considered malformed; if provided anyway, `A` is rounded down to the lowest
    valid multiple of `S`.
* `D`, the data value to write. If the amount of data exceeds `S` bytes, the
    written data will be truncated to the lower bits.
* `W`, the write signal, pulsed. Can be 1 tick in duration. Writes the value of
    `D` with size `S` to address `A`.
* `R`, the read signal, pulsed. Can be 1 tick in duration. Reads the stored
    value with size `S` from address `A`.

When read is pulsed, the reconstructed number is output as signal `R` on the red
output wire for a single tick, which can then be stored in a memory cell if
needed for longer periods.
"""


def main():
    # Parse args

    # The list of bytes we wish to encode into the blueprint.
    encoded_data = list(range(256))

    pass


if __name__ == "__main__":
    main()
