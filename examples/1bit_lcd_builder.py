# 32belt_font_encoder.py

"""
Constructs a 1-bit LCD text-mode screen, which can be used to display any 
message using the standard ASCII characters. In summary, this program:

1. Reads a font bitmap image, and encodes the pixels of each character 
    lengthwise into a single 32 bit integer;
2. Constructs a converter blueprint which takes a position and a ascii character
    code and returns an encoded set of bitwise signals
3. Creates the desired LCD screen blueprint for which everything can be hooked
    up to it
"""

from draftsman.blueprintable import Blueprint, BlueprintBook

from draftsman.data import signals

from PIL import Image


def main():
    # Parameters of the screen we're making
    target_lcd_width = 180
    target_lcd_height = 120
    font_width = 5
    font_height = 6

    # TODO: ensure we're in a vanilla configuration

    # First, we need to create an indexing list so we know which numeric values
    # correspond to
    lcd_index = []
    # We want to exclude color signals as they'll pollute the LCD's encoding
    color_signals = {
        "signal-red",
        "signal-green",
        "signal-blue",
        "signal-yellow",
        "signal-pink",
        "signal-cyan",
        "signal-white",
    }
    lcd_index += [signal for signal in signals.virtual if signal not in color_signals]
    lcd_index += signals.item
    lcd_index += signals.fluid
    print(lcd_index)
    print(len(lcd_index))

    assert target_lcd_width <= len(lcd_index)

    # Determine the text writing cell indexing
    text_memory_index = signals.virtual + signals.item + signals.fluid

    # characters_per_row = target_lcd_width // font_width
    # characters_per_column = target_lcd_height // font_height
    # assert characters_per_row * characters_per_column <= len(text_memory_index), "{}".format(characters_per_row * characters_per_column)

    blueprint = Blueprint()

    font_image = Image.open("examples/assets/32belt.png")
    im_width, im_height = font_image.size
    pix = font_image.load()
    for y in range(0, im_height, 7):
        for x in range(0, im_width, 6):
            print(pix[x, y])

    encoded_font = []
    for ascii_index in range(128):
        x = ascii_index % 32 * (font_width + 1)
        y = ascii_index // 32 * (font_height + 1)
        # We want to encode by columns instead of rows, so we traverse x first
        i = 0
        ascii_char = 0
        for sx in range(font_width):
            for sy in range(font_height):
                bit_set = pix[x + sx, y + sy] == (255, 255, 255, 255)
                ascii_char |= bit_set << i
                i += 1

        print(ascii_char)
        encoded_font.append(ascii_char)

    print(encoded_font[64])

    print(blueprint.to_string())

    pass


if __name__ == "__main__":
    main()
