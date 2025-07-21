import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_font_atlas(
    font_name: str = "Arial.ttf",
    font_size: int = 72,
    atlas_size: int = 512,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.,:;!?-+=/\\|#()[]{}*&$%^@~",
) -> tuple[np.ndarray, dict]:
    """
    Create a font atlas from a font file

    Args:
        font_path: path to the font file
        font_size: font size
        atlas_size: atlas size (512x512, 1024x1024, etc.)

    Returns:
        Tuple (atlas texture, atlas info)
    """

    # Create an empty texture
    atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    font = ImageFont.truetype(font_name, font_size)

    atlas_info = {}
    max_height = 0
    min_top_padding = None

    for char in chars:
        bbox = draw.textbbox((0, 0), char, font=font)
        if min_top_padding is None or bbox[1] < min_top_padding:
            min_top_padding = bbox[1]
        if max_height < bbox[3] - bbox[1]:
            max_height = bbox[3] - bbox[1]

    x, y = 0, -min_top_padding
    row = 1
    for char in chars:
        # Get the size of the character
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]

        # Check if the character fits in the current row
        if x + char_width > atlas_size:
            x = 0
            y += max_height
            row += 1

        # Draw the character
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))

        # Save the character information
        atlas_info[char] = {
            "uv_min": (x / atlas_size, (atlas_size - (row * max_height)) / atlas_size),
            "uv_max": ((x + char_width) / atlas_size, (atlas_size - ((row - 1) * max_height)) / atlas_size),
            "width": char_width,
            "height": max_height,
        }

        x += char_width

    atlas.save("font_atlas.png")

    return np.array(atlas), atlas_info
