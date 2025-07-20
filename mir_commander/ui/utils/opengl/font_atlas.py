import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_font_atlas(
    font_name: str,
    font_size: int = 150,
    atlas_size: int = 1024,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
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
    x, y = 0, 0
    max_height = 0
    
    for char in chars:
        # Get the size of the character
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        
        # Check if the character fits in the current row
        if x + char_width > atlas_size:
            x = 0
            y += max_height
            max_height = 0
        
        # Draw the character
        draw.text((x, y), char, font=font, fill=(255, 255, 255, 255))
        
        # Save the character information
        atlas_info[char] = {
            "uv_min": (x / atlas_size, y / atlas_size),
            "uv_max": ((x + char_width) / atlas_size, (y + char_height) / atlas_size),
            "width": char_width,
            "height": char_height,
        }
        
        x += char_width
        max_height = max(max_height, char_height)
    
    return np.array(atlas), atlas_info
