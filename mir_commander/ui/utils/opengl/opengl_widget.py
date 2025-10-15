import logging

import numpy as np
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QVector3D, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

from mir_commander.utils.consts import DIR

from . import shaders
from .action_handler import ActionHandler
from .enums import ClickAndMoveMode, PaintMode, ProjectionMode, WheelMode
from .errors import NodeNotFoundError
from .keymap import Keymap
from .models import rect
from .projection import ProjectionManager
from .renderer import Renderer
from .resource_manager import (
    Camera,
    FontAtlas,
    FragmentShader,
    ResourceManager,
    ShaderProgram,
    Texture2D,
    VertexArrayObject,
    VertexShader,
)
from .resource_manager.font_atlas import create_font_atlas
from .scene import Node, Scene
from .utils import Color4f, color_to_id

logger = logging.getLogger("OpenGLWidget")


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget, keymap: None | Keymap = None):
        super().__init__(parent)

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._rotation_speed = 0.5
        self._scale_speed = 1.0

        # Initialize components
        self.action_handler = ActionHandler(keymap)
        self.projection_manager = ProjectionManager(width=self.size().width(), height=self.size().height())
        self.resource_manager = ResourceManager(Camera("main"), Scene("main"))
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
        self.add_font_atlas(font_path=str(DIR.FONTS / "DejaVuSansCondensed-Bold.ttf"), font_atlas_name="default")

    def release_opengl(self):
        self.makeCurrent()
        self.renderer.release()
        self.resource_manager.release()

    def init_shaders(self):
        self.resource_manager.add_shader(
            ShaderProgram(
                "default",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED),
                FragmentShader(shaders.fragment.BLINN_PHONG),
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "text",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED_BILLBOARD),
                FragmentShader(shaders.fragment.TEXTURE),
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "transparent_flat",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED),
                FragmentShader(shaders.fragment.WBOIT_TRANSPARENT_FLAT),
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "transparent",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED),
                FragmentShader(shaders.fragment.WBOIT_TRANSPARENT),
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram("picking", VertexShader(shaders.vertex.PICKING), FragmentShader(shaders.fragment.PICKING))
        )

    def add_font_atlas(self, font_path: str, font_atlas_name: str):
        atlas_size = 4096
        font_size = 480
        data, font_atlas = create_font_atlas(font_atlas_name, font_path, font_size=font_size, atlas_size=atlas_size)
        texture = Texture2D(name=f"font_atlas_{font_atlas_name}")
        texture.init(width=atlas_size, height=atlas_size, data=data, use_mipmaps=True)
        self.resource_manager.add_font_atlas(font_atlas)
        self.resource_manager.add_texture(texture)

        self._build_font_atlas_geometry(font_atlas)

    def _build_font_atlas_geometry(self, font_atlas: FontAtlas):
        for char, info in font_atlas.chars.items():
            u_min, v_min = info.u_min, info.v_min
            u_max, v_max = info.u_max, info.v_max
            width = info.width / info.height

            vertices = rect.get_vertices(left=-width, right=width, bottom=-1.0, top=1.0)
            tex_coords = rect.get_texture_coords(u_min=u_min, u_max=u_max, v_min=v_min, v_max=v_max)
            vao = VertexArrayObject(f"font_atlas_{font_atlas.name}_{char}", vertices, rect.get_normals(), tex_coords)
            self.resource_manager.add_vertex_array_object(vao)

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
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    @property
    def scene_rotation(self) -> tuple[float, float, float]:
        return self.resource_manager.current_scene.transform.rotation_angles

    def get_scene_scale(self) -> float:
        return self.resource_manager.current_scene.transform.get_scale().x()

    def resizeGL(self, w: int, h: int):
        self.makeCurrent()
        self.projection_manager.build_projections(w, h)
        self.renderer.resize(w, h, self.devicePixelRatio())
        self.update()

    def paintGL(self):
        self.makeCurrent()
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

    def set_scene_position(self, point: QVector3D):
        self.resource_manager.current_scene.transform.set_position(point)
        self.update()

    def set_scene_translate(self, vector: QVector3D):
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

        self.resource_manager.current_scene.transform.scale(QVector3D(factor, factor, factor))
        self.update()

    def set_scene_scale(self, factor: float):
        if factor == 0.0:
            return

        self.resource_manager.current_scene.transform.set_scale(QVector3D(factor, factor, factor))
        self.update()

    def new_cursor_position(self, x: int, y: int):
        pass

    def render_to_image(
        self, width: int, height: int, transparent_bg: bool = False, crop_to_content: bool = False
    ) -> np.ndarray:
        self.makeCurrent()
        return self.renderer.render_to_image(width, height, transparent_bg, crop_to_content)

    def node_under_cursor(self) -> Node:
        self.makeCurrent()
        image = self.renderer.picking_image()

        x = self._cursor_pos.x()
        y = self._cursor_pos.y()

        color = image.pixelColor(x, y)
        picking_id = color_to_id(color)

        return self.resource_manager.current_scene.find_node_by_picking_id(picking_id)

    def set_node_color_by_id(self, node_id: int, color: Color4f):
        try:
            node = self.resource_manager.current_scene.main_node.get_node_by_id(node_id)
            node.set_color(color)
            self.update()
        except NodeNotFoundError:
            logger.debug("Can't set node color: node `%d` not found", node_id)

    def set_node_visible(
        self, node_id: int, visible: bool, apply_to_parents: bool = False, apply_to_children: bool = False
    ):
        try:
            node = self.resource_manager.current_scene.main_node.get_node_by_id(node_id)
            node.set_visible(visible, apply_to_parents=apply_to_parents, apply_to_children=apply_to_children)
            self.update()
        except NodeNotFoundError:
            logger.debug("Can't set node visible: node `%d` not found", node_id)

    def remove_node(self, node_id: int):
        self.makeCurrent()
        try:
            node = self.resource_manager.current_scene.main_node.get_node_by_id(node_id)
            node.remove()
            self.update()
        except NodeNotFoundError:
            logger.debug("Can't remove node: node `%d` not found", node_id)
