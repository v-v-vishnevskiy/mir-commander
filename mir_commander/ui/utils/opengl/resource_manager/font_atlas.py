import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel


class CharInfo(BaseModel):
    width: int
    height: int
    u_min: float
    u_max: float
    v_min: float
    v_max: float


class FontAtlas(BaseModel):
    name: str
    chars: dict[str, CharInfo]


def create_font_atlas(
    name: str,
    file: str,
    font_size: int = 124,
    atlas_size: int = 1024,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.,:;!?-+=/\\|#()[]{}*&$%^@~",
) -> tuple[np.ndarray, FontAtlas]:
    """
    Create a font atlas from a font file
    """

    # Create an empty texture
    atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    font = ImageFont.truetype(file, font_size)

    atlas_info = FontAtlas(name=name, chars={})
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
        char_width = int(bbox[2] - bbox[0])

        # Check if the character fits in the current row
        if x + char_width > atlas_size:
            x = 0
            y += max_height
            row += 1

        # Draw the character
        draw.text((x - bbox[0], y), char, font=font, fill=(255, 255, 255, 255))

        # Save the character information
        atlas_info.chars[char] = CharInfo(
            width=char_width,
            height=max_height,
            u_min=x / atlas_size,
            u_max=(x + char_width) / atlas_size,
            v_min=(atlas_size - (row * max_height)) / atlas_size,
            v_max=(atlas_size - ((row - 1) * max_height)) / atlas_size,
        )

        x += char_width + 1

    return np.array(atlas), atlas_info
