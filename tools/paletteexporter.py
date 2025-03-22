import math
import sys
from PIL import Image
from PIL import ImageDraw

COLOR_SQUARES_PER_LINE = 16
# In pixels.
COLOR_SQUARE_SIZE = 1

COLOR_RAMP_TYPE = "SonLVL"

# Color ramp used by SonLVL.
SONLVL_COLOR_RAMP = [0x00, 0x24, 0x49, 0x6D, 0x92, 0xB6, 0xDB, 0xFF]

OUTPUT_FILE_PATH = "output.png"


def open_file():
    filepath = sys.argv[1]
    with open(filepath, "rb") as file:
        colors_array = []
        # A single color is represented in 2 bytes.
        while color_bytes := file.read(2):
            color_rgb = bytes_to_rgba(color_bytes)
            colors_array.append(color_rgb)
        generate_output_img(colors_array)

def convert_channel(channel):
    if COLOR_RAMP_TYPE == "SonLVL":
        return SONLVL_COLOR_RAMP[channel // 2]
    elif COLOR_RAMP_TYPE == "KegaFusion":
        return channel << 4
    elif COLOR_RAMP_TYPE == "EXTEND":
        # 0x0A -> 0xAA
        return (channel << 4) | channel


def bytes_to_rgba(color_bytes):
    # Refer to:
    # https://segaretro.org/Sega_Mega_Drive/Palettes_and_CRAM#Format
    first_byte = color_bytes[0]
    second_byte = color_bytes[1]
    val_red = second_byte & 0x0F
    val_green = (second_byte & 0xF0) >> 4
    val_blue = first_byte & 0x0F
    # print(f"{val_red:#0x}, {val_green:#0x}, {val_blue:#0x}")
    return convert_channel(val_red), convert_channel(val_green), convert_channel(val_blue), 255


def generate_output_img(colors_array):
    img_width = COLOR_SQUARE_SIZE * min(COLOR_SQUARES_PER_LINE, len(colors_array))
    img_height = math.ceil(len(colors_array) / COLOR_SQUARES_PER_LINE) * COLOR_SQUARE_SIZE
    print(f"Generating output palette image! Number of colors: {len(colors_array)}, width: {img_width}, height: {img_height}")
    output_img = Image.new("RGBA", [img_width, img_height], (0, 0, 0, 0))
    xpos = 0
    ypos = 0
    for index, color in enumerate(colors_array):
        # Check if we move to the next row.
        if index % COLOR_SQUARES_PER_LINE == 0:
            xpos = 0
            ypos = math.ceil(index / COLOR_SQUARES_PER_LINE) * COLOR_SQUARE_SIZE

        edit_img = ImageDraw.Draw(output_img)
        edit_img.rectangle([(xpos, ypos),(xpos + COLOR_SQUARE_SIZE - 1, ypos + COLOR_SQUARE_SIZE - 1)], color, color)
        xpos += COLOR_SQUARE_SIZE

    print("Palette image generated! Saving to " + OUTPUT_FILE_PATH)
    output_img.save(OUTPUT_FILE_PATH)



if __name__ == '__main__':
    open_file()
