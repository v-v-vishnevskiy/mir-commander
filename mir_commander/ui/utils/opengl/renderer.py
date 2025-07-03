import logging

from OpenGL.GL import glClear, glClearColor, glLoadMatrixf, GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from .camera import Camera
from .graphics_items.item import Item
from .utils import Color4f

logger = logging.getLogger("OpenGL.Renderer")


class Renderer:
    def __init__(self, camera: Camera):
        self._camera = camera
        self._items: set[Item] = set()
        self._bg_color = (0.0, 0.0, 0.0, 1.0)

    def add_item(self, item: Item):
        if not issubclass(type(item), Item):
            logger.error("Invalid item type: %s", item.__class__.__name__)
            return
        self._items.add(item)

    def remove_item(self, item: Item):
        self._items.remove(item)

    def clear(self):
        for item in self._items:
            item.clear()
        self._items.clear()

    def set_background_color(self, color: Color4f):
        self._bg_color = color

    def paint(self):
        glLoadMatrixf(self._camera.translation_matrix.data())
        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        for item in self._items:
            item.paint()

    def point_to_line(self, x: int, y: int, width: int, height: int) -> tuple[QVector3D, QVector3D]:
        viewport = QRect(0, 0, width, height)
        y = height - y  # opengl computes from left-bottom corner
        return (
            QVector3D(x, y, -1.0).unproject(
                self._camera.translation_matrix, 
                self._camera.projection_matrix, 
                viewport
            ),
            QVector3D(x, y, 1.0).unproject(
                self._camera.translation_matrix, 
                self._camera.projection_matrix, 
                viewport
            ),
        )

    def crop_image_to_content(self, image: QImage, bg_color: QColor) -> QImage:
        # Need this hack with the fake 1x1 image to take into account the format of our real image
        # so we know the value of the background color as it is represented in the image.
        bg_image = QImage(1, 1, image.format())
        bg_image.setPixelColor(0, 0, bg_color)
        bg_color_value = bg_image.pixel(0, 0)
        xmin = ymin = xmax = ymax = -1

        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixel(x, y) != bg_color_value:
                    ymin = y
                    break
            if ymin >= 0:
                break

        for y in reversed(range(image.height())):
            for x in range(image.width()):
                if image.pixel(x, y) != bg_color_value:
                    ymax = y
                    break
            if ymax >= 0:
                break

        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixel(x, y) != bg_color_value:
                    xmin = x
                    break
            if xmin >= 0:
                break

        for x in reversed(range(image.width())):
            for y in range(image.height()):
                if image.pixel(x, y) != bg_color_value:
                    xmax = x
                    break
            if xmax >= 0:
                break

        if xmin >= 0 and xmax >= 0 and ymin >= 0 and ymax >= 0:
            crop_area = QRect(xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)
            image = image.copy(crop_area)

        return image

    def render_to_image(
        self, 
        width: int, 
        height: int, 
        transparent_bg: bool = False, 
        crop_to_content: bool = False,
        make_current_callback=None
    ) -> QImage:
        if make_current_callback:
            make_current_callback()

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setSamples(16)
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        bg_color_bak = self._bg_color

        if transparent_bg:
            self._bg_color = bg_color_bak[0], bg_color_bak[1], bg_color_bak[2], 0.0

        bg_color = QColor.fromRgbF(*self._bg_color)

        from OpenGL.GL import glViewport
        glViewport(0, 0, width, height)
        self.paint()
        self._bg_color = bg_color_bak

        fbo.release()

        image = fbo.toImage()

        if not transparent_bg:
            image = image.convertToFormat(QImage.Format_RGB32)

        if crop_to_content:
            image = self.crop_image_to_content(image, bg_color)

        return image
