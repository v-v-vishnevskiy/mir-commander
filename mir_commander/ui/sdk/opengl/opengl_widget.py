import logging

import numpy as np
from PySide6.QtCore import QFile, QPoint, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.camera import Camera
from mir_commander.core.graphics.font_atlas import FontAtlas, create_font_atlas
from mir_commander.core.graphics.mesh import rect
from mir_commander.core.graphics.opengl.renderer import PaintMode, Renderer
from mir_commander.core.graphics.opengl.texture2d import Texture2D
from mir_commander.core.graphics.opengl.vertex_array_object import VertexArrayObject
from mir_commander.core.graphics.projection import ProjectionManager, ProjectionMode
from mir_commander.core.graphics.resource_manager import ResourceManager
from mir_commander.core.graphics.scene.node import Node
from mir_commander.core.graphics.scene.scene import Scene
from mir_commander.core.graphics.utils import Color4f, color_to_id

from .action_handler import ActionHandler
from .enums import ClickAndMoveMode, WheelMode
from .keymap import Keymap

logger = logging.getLogger("UI.SDK.OpenGLWidget")


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, keymap: None | Keymap = None):
        super().__init__()

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._rotation_speed = 0.5
        self._scale_speed = 1.0

        # Initialize components
        self.action_handler = ActionHandler(keymap)
        self.projection_manager = ProjectionManager(width=self.size().width(), height=self.size().height())
        self.resource_manager = ResourceManager()
        self.resource_manager.add_camera("main", Camera(), make_current=True)
        self.resource_manager.add_scene("main", Scene(), make_current=True)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.init_actions()

    def initializeGL(self):
        try:
            self.init_opengl()
        except Exception as e:
            logger.error("Failed to initialize OpenGL: %s", e)

    def init_opengl(self):
        self.renderer = Renderer(self.projection_manager, self.resource_manager)
        self.renderer.resize(self.size().width(), self.size().height(), self.devicePixelRatio())
        self.init_shaders()

        font = QFile(":/core/fonts/Inter-Bold.ttf")
        if font.open(QFile.OpenModeFlag.ReadOnly):
            self.add_font_atlas(font_data=font.readAll().data(), font_atlas_name="default")
        else:
            logger.error("Failed to open font file: %s", font.errorString())

    def release_opengl(self):
        self.makeCurrent()
        self.renderer.release()
        self.resource_manager.release()

    def init_shaders(self):
        pass

    def add_font_atlas(self, font_data: bytes, font_atlas_name: str):
        atlas_size = 4096
        font_size = 470
        data, font_atlas = create_font_atlas(
            font_data, font_size=font_size, atlas_size=atlas_size, padding=3, debug=False
        )
        texture = Texture2D()
        texture.init(width=atlas_size, height=atlas_size, data=data, use_mipmaps=True)
        self.resource_manager.add_font_atlas(font_atlas_name, font_atlas)
        self.resource_manager.add_texture(f"font_atlas_{font_atlas_name}", texture)

        self._build_font_atlas_geometry(font_atlas, font_atlas_name)

    def _build_font_atlas_geometry(self, font_atlas: FontAtlas, font_atlas_name: str):
        for char, info in font_atlas.chars.items():
            u_min, v_min = info.u_min, info.v_min
            u_max, v_max = info.u_max, info.v_max
            width = info.width / info.height

            vertices = rect.get_vertices(left=-width, right=width, bottom=-1.0, top=1.0)
            tex_coords = rect.get_texture_coords(u_min=u_min, u_max=u_max, v_min=v_min, v_max=v_max)
            vao = VertexArrayObject(vertices, rect.get_normals(), tex_coords)
            self.resource_manager.add_vertex_array_object(f"font_atlas_{font_atlas_name}_{char}", vao)

    def clear(self):
        self.resource_manager.current_scene.clear()

    def init_actions(self):
        self.action_handler.add_action("rotate_up", True, self.rotate_scene, -1.0 * self._rotation_speed, 0.0, 0.0)
        self.action_handler.add_action("rotate_down", True, self.rotate_scene, 1.0 * self._rotation_speed, 0.0, 0.0)
        self.action_handler.add_action("rotate_left", True, self.rotate_scene, 0.0, -1.0 * self._rotation_speed, 0.0)
        self.action_handler.add_action("rotate_right", True, self.rotate_scene, 0.0, 1.0 * self._rotation_speed, 0.0)
        self.action_handler.add_action("zoom_in", True, self.scale_scene, 1.0 + 0.05 * self._scale_speed)
        self.action_handler.add_action("zoom_out", True, self.scale_scene, 1.0 - 0.05 * self._scale_speed)

    @property
    def background_color(self) -> Color4f:
        return self.renderer.background_color

    @property
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    @property
    def scene_rotation(self) -> tuple[float, float, float]:
        return self.resource_manager.current_scene.transform.rotation_angles

    def get_scene_scale(self) -> float:
        return self.resource_manager.current_scene.transform.get_scale().x

    def resizeGL(self, w: int, h: int):
        self.projection_manager.build_projections(w, h)
        self.renderer.resize(w, h, self.devicePixelRatio())
        self.update()

    def paintGL(self):
        self.renderer.paint(PaintMode.Normal, self.defaultFramebufferObject())

    def keyPressEvent(self, event: QKeyEvent):
        self.action_handler.call_action(event, self.action_handler.keymap.match_key_event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self.action_handler.stop_action(event, self.action_handler.keymap.match_key_event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = pos - self._cursor_pos
                self.rotate_scene(self._rotation_speed * diff.y(), self._rotation_speed * diff.x(), 0.0)
        else:
            self.new_cursor_position(pos.x(), pos.y())

        self._cursor_pos = pos

    def mousePressEvent(self, event: QMouseEvent):
        self.action_handler.call_action(event, self.action_handler.keymap.match_mouse_event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.action_handler.stop_action(event, self.action_handler.keymap.match_mouse_event)

    def wheelEvent(self, event: QWheelEvent):
        events: list[str] = []
        delta = event.angleDelta().x()
        if delta > 0:
            events.append("wheel_left")
        elif delta < 0:
            events.append("wheel_right")

        delta = event.angleDelta().y()
        if delta > 0:
            events.append("wheel_up")
        elif delta < 0:
            events.append("wheel_down")

        for e in events:
            self.action_handler.call_action(event=e, match_fn=self.action_handler.keymap.match_wheel_event)

    def set_projection_mode(self, mode: ProjectionMode):
        self.makeCurrent()
        self.projection_manager.set_projection_mode(mode)
        self.renderer.resize(self.size().width(), self.size().height(), self.devicePixelRatio())
        self.update()

    def toggle_projection_mode(self):
        self.makeCurrent()
        self.projection_manager.toggle_projection_mode()
        self.renderer.resize(self.size().width(), self.size().height(), self.devicePixelRatio())
        self.update()

    def set_perspective_projection_fov(self, value: float):
        self.makeCurrent()
        self.projection_manager.perspective_projection.set_fov(value)
        self.projection_manager.build_projections(self.size().width(), self.size().height())
        self.renderer.resize(self.size().width(), self.size().height(), self.devicePixelRatio())
        self.update()

    def set_scene_position(self, point: Vector3D):
        self.resource_manager.current_scene.transform.set_position(point)
        self.update()

    def set_scene_translate(self, vector: Vector3D):
        self.resource_manager.current_scene.transform.translate(vector)
        self.update()

    def set_background_color(self, color: Color4f):
        self.renderer.set_background_color(color)
        self.update()

    def rotate_scene(self, pitch: float, yaw: float, roll: float):
        if pitch == 0.0 and yaw == 0.0 and roll == 0.0:
            return

        self.resource_manager.current_scene.transform.rotate(pitch, yaw, roll)
        self.update()

    def set_scene_rotation(self, pitch: float, yaw: float, roll: float):
        self.resource_manager.current_scene.transform.set_rotation(pitch, yaw, roll)
        self.update()

    def scale_scene(self, factor: float):
        if factor == 1.0 or factor == 0.0:
            return

        self.resource_manager.current_scene.transform.scale(Vector3D(factor, factor, factor))
        self.update()

    def set_scene_scale(self, factor: float):
        if factor == 0.0:
            return

        self.resource_manager.current_scene.transform.set_scale(Vector3D(factor, factor, factor))
        self.update()

    def new_cursor_position(self, x: int, y: int):
        pass

    def render_to_image(
        self, width: int, height: int, bg_color: Color4f | None = None, crop_to_content: bool = False
    ) -> np.ndarray:
        self.makeCurrent()
        return self.renderer.render_to_image(width, height, bg_color, crop_to_content)

    def node_under_cursor(self) -> Node:
        self.makeCurrent()
        image = self.renderer.picking_image()

        try:
            color = image[self._cursor_pos.y(), self._cursor_pos.x()]
        except IndexError:
            color = (0, 0, 0)
        picking_id = color_to_id(int(color[0]), int(color[1]), int(color[2]))

        return self.resource_manager.current_scene.find_node_by_picking_id(picking_id)
