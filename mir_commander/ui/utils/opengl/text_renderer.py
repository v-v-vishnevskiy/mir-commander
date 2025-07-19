from PySide6.QtGui import QFont, QPainter, QImage, QColor
from PySide6.QtCore import Qt

from .utils import crop_image_to_content


def render_text_to_image(text: str, font: None | QFont = None, padding: int = 0) -> QImage:
    if font is None:
        font = QFont()
        font.setPointSize(150)
        font.setBold(False)
        font.setFamily("Arial")

    # Create temporary image for measuring text size
    temp_image = QImage(1, 1, QImage.Format.Format_RGBA8888)
    temp_painter = QPainter(temp_image)
    temp_painter.setFont(font)
    text_rect = temp_painter.boundingRect(0, 0, 1000, 1000, Qt.AlignLeft | Qt.AlignTop, text)
    temp_painter.end()

    # Add padding
    width = text_rect.width() + padding * 2
    height = text_rect.height() + padding * 2

    # Ensure minimum size
    if width <= 0:
        width = 1
    if height <= 0:
        height = 1

    # Create image with white background for debugging
    image = QImage(width, height, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))  # Transparent background

    # Render text
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Draw text
    text_color = QColor(0, 0, 0, 255)  # Black text
    painter.setPen(text_color)
    painter.setFont(font)

    # Position text correctly
    x = padding
    y = padding + text_rect.height() - text_rect.y()  # Adjust for baseline

    painter.drawText(x, y, text)

    painter.end()

    return crop_image_to_content(image, QColor(0, 0, 0, 0))
