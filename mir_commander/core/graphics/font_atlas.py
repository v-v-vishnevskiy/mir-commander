import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
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
    font_data: bytes,
    font_size: int = 124,
    atlas_size: int = 1024,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.,:;!?–-+±=/\\|#()[]{}<>*&$%^@~§'\"`",
    padding: int = 1,
    debug: bool = False,
) -> tuple[np.ndarray, FontAtlas]:
    """
    Create a font atlas from a font file
    """

    # Create an empty texture
    atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    font = ImageFont.truetype(BytesIO(font_data), font_size)

    atlas_info = FontAtlas(chars={})

    bbox = draw.textbbox((0, 0), chars[0], font=font)
    max_height = bbox[3]
    for char in chars[1:]:
        bbox = draw.textbbox((0, 0), char, font=font)
        if max_height < bbox[3]:
            max_height = bbox[3]

    x, y = 0, 0
    for char in chars:
        # Get the size of the character
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]

        # Check if the character fits in the current row
        if x + char_width + padding > atlas_size:
            x = 0
            y += max_height + padding  # type: ignore[assignment]

        # Draw the character
        draw.text((x - bbox[0], y), char, font=font, fill=(255, 255, 255, 255))

        # Save the character information
        atlas_info.chars[char] = CharInfo(
            width=char_width,
            height=max_height,
            u_min=x / atlas_size,
            u_max=(x + char_width) / atlas_size,
            v_min=1.0 - ((y + max_height) / atlas_size),
            v_max=1.0 - (y / atlas_size),
        )

        x += char_width + padding  # type: ignore[assignment]

    if debug:
        # Draw UV coordinate boundaries for debugging
        draw = ImageDraw.Draw(atlas)
        for char_info in atlas_info.chars.values():
            x1 = int(char_info.u_min * atlas_size)
            x2 = int(char_info.u_max * atlas_size)
            y1 = int((1.0 - char_info.v_max) * atlas_size)
            y2 = int((1.0 - char_info.v_min) * atlas_size)

            # Draw rectangle boundaries in red
            draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 255), width=1)

        atlas.save("font_atlas.png")

    return np.array(atlas), atlas_info
