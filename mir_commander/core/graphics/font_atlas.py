import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel


class CharInfo(BaseModel):
    width: float
    height: float
    u_min: float
    u_max: float
    v_min: float
    v_max: float


class FontAtlas(BaseModel):
    chars: dict[str, CharInfo]


def create_font_atlas(
    file: str,
    font_size: int = 124,
    atlas_size: int = 1024,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.,:;!?–-+±=/\\|#()[]{}<>*&$%^@~§'\"`",
) -> tuple[np.ndarray, FontAtlas]:
    """
    Create a font atlas from a font file
    """

    # Create an empty texture
    atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    font = ImageFont.truetype(file, font_size)

    atlas_info = FontAtlas(chars={})

    bbox = draw.textbbox((0, 0), chars[0], font=font)
    min_top_padding = bbox[1]
    max_height = bbox[3] - bbox[1]
    for char in chars[1:]:
        bbox = draw.textbbox((0, 0), char, font=font)
        if bbox[1] < min_top_padding:
            min_top_padding = bbox[1]
        if max_height < bbox[3] - bbox[1]:
            max_height = bbox[3] - bbox[1]

    width_padding = 1.0
    height_padding = min_top_padding + 1.0

    x, y = width_padding, -min_top_padding + height_padding
    for char in chars:
        # Get the size of the character
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]

        # Check if the character fits in the current row
        if x + char_width + width_padding > atlas_size:
            x = width_padding
            y += max_height + height_padding

        # Draw the character
        draw.text((x - bbox[0], y), char, font=font, fill=(255, 255, 255, 255))

        # Save the character information
        atlas_info.chars[char] = CharInfo(
            width=char_width,
            height=max_height + height_padding,
            u_min=x / atlas_size,
            u_max=(x + char_width) / atlas_size,
            v_min=(atlas_size - (y + max_height + height_padding)) / atlas_size,
            v_max=(atlas_size - y) / atlas_size,
        )

        x += char_width + width_padding

    return np.array(atlas), atlas_info
