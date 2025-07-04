import logging

from OpenGL.GL import glClear, glClearColor, GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT, glLoadIdentity
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from .projection import ProjectionManager
from .utils import Color4f
from .scene import Scene

logger = logging.getLogger("OpenGL.Renderer")


class Renderer:
    def __init__(self, projection_manager: ProjectionManager, scene: Scene):
        self._projection_manager = projection_manager
        self._scene = scene
        self._bg_color = (0.0, 0.0, 0.0, 1.0)

    def set_background_color(self, color: Color4f):
        self._bg_color = color

    def paint(self):
        glLoadIdentity()
        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        self._scene.paint()

    def point_to_line(self, x: int, y: int, width: int, height: int) -> tuple[QVector3D, QVector3D]:
        viewport = QRect(0, 0, width, height)
        y = height - y  # opengl computes from left-bottom corner

        # Get near and far plane values for unprojection calculations
        near_plane, far_plane = self._projection_manager.active_projection._get_near_far_planes()

        projection_matrix = self._projection_manager.active_projection.matrix
        near_point = QVector3D(x, y, near_plane).unproject(self._scene.transform, projection_matrix, viewport)
        far_point = QVector3D(x, y, far_plane).unproject(self._scene.transform, projection_matrix, viewport)

        # Return the near point and the direction vector from near to far
        direction = far_point - near_point
        return near_point, direction

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
