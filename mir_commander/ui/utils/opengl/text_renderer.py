from PySide6.QtGui import QFont, QPainter, QImage, QColor
from PySide6.QtCore import Qt


def calculate_font_size(font: QFont, target_size: int, text: str) -> int:
    """Calculate optimal font size to fit text in square"""

    # Start with a reasonable font size
    font.setPointSize(target_size // 4)

    # Create temporary painter to measure text
    temp_image = QImage(1, 1, QImage.Format.Format_RGBA8888)
    temp_painter = QPainter(temp_image)
    temp_painter.setFont(font)

    # Binary search for optimal font size
    min_size = 1
    max_size = target_size
    optimal_size = min_size

    while min_size <= max_size:
        current_size = (min_size + max_size) // 2
        font.setPointSize(current_size)
        temp_painter.setFont(font)

        # Measure text bounds
        text_rect = temp_painter.boundingRect(0, 0, target_size, target_size, Qt.AlignCenter, text)

        # Check if text fits
        if text_rect.width() <= target_size * 0.9 and text_rect.height() <= target_size * 0.9:
            optimal_size = current_size
            min_size = current_size + 1
        else:
            max_size = current_size - 1

    temp_painter.end()
    return optimal_size


def render_text_to_image(
    text: str,
    font: None | QFont = None,
    color: QColor = QColor(255, 255, 255, 255),
    size: int = 100,
) -> QImage:
    if font is None:
        font = QFont()
        font.setBold(False)
        font.setFamily("Arial")

    # Create square image with specified size
    image = QImage(size, size, QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))  # Transparent background

    # Calculate and set optimal font size
    optimal_font_size = calculate_font_size(font, size, text)
    font.setPointSize(optimal_font_size)

    # Render text
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    painter.setPen(color)
    painter.setFont(font)

    # Center text in the square
    painter.drawText(0, 0, size, size, Qt.AlignCenter, text)

    painter.end()

    return image
