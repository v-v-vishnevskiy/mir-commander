import logging

from OpenGL.GL import GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT, glClear, glClearColor, glViewport, glEnable, glDisable, GL_BLEND, GL_DEPTH_TEST, GL_CULL_FACE, glUseProgram, glUniformMatrix4fv, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from ..camera import Camera
from ..enums import PaintMode
from ..graphics_items.item import Item
from ..projection import ProjectionManager
from ..scene_graph import SceneGraph
from ..utils import Color4f

logger = logging.getLogger("OpenGL.Renderer")


class BaseRenderer:
    def __init__(self, projection_manager: ProjectionManager, scene: SceneGraph, camera: Camera):
        self._projection_manager = projection_manager
        self._scene = scene
        self._camera = camera
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self._picking_image: None | QImage = None
        self._has_new_image = False
        self._shaders = {}
        self.init_shaders()

    def init_shaders(self):
        pass

    def set_background_color(self, color: Color4f):
        self._bg_color = color

    def paint(self, paint_mode: PaintMode):
        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glDisable(GL_BLEND)

        if paint_mode == PaintMode.Picking:
            self.paint_picking(self._scene.picking_items())
        else:
            opaque_items, transparent_items = self._scene.items()

            self.paint_opaque(opaque_items)

            if transparent_items:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                self.paint_transparent(self._sort_by_depth(transparent_items))

            self._has_new_image = False

    def paint_opaque(self, items: list[Item]):
        pass

    def paint_transparent(self, items: list[Item]):
        pass

    def paint_picking(self, items: list[Item]):
        pass

    def _get_item_depth(self, item: Item) -> float:
        point = QVector3D(0.0, 0.0, 0.0) * item.get_transform
        return self._camera.position.distanceToPoint(point)

    def _sort_by_depth(self, items: list[Item]) -> list[Item]:
        return sorted(items, key=self._get_item_depth, reverse=True)

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

        glViewport(0, 0, width, height)

        self.paint(PaintMode.Normal)

        self._bg_color = bg_color_bak

        fbo.release()

        image = fbo.toImage()

        if not transparent_bg:
            image = image.convertToFormat(QImage.Format_RGB32)

        if crop_to_content:
            image = self.crop_image_to_content(image, bg_color)

        return image

    def picking_image(self, width: int, height: int) -> QImage:
        if self._has_new_image:
            return self._picking_image

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        glViewport(0, 0, width, height)

        self.paint(PaintMode.Picking)

        fbo.release()

        self._picking_image = fbo.toImage()
        self._has_new_image = True

        return self._picking_image
