import logging
import traceback

from OpenGL.GL import GL_MULTISAMPLE, glEnable, glViewport
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QVector3D, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from . import shaders
from .action_handler import ActionHandler
from .enums import ClickAndMoveMode, PaintMode, ProjectionMode, WheelMode
from .font_atlas import create_font_atlas
from .keymap import Keymap
from .models import rect
from .projection import ProjectionManager
from .renderer import Renderer
from .resource_manager import (
    Camera,
    FontAtlas,
    FragmentShader,
    Mesh,
    ResourceManager,
    Scene,
    SceneNode,
    ShaderProgram,
    Texture2D,
    VertexArrayObject,
    VertexShader,
)
from .utils import Color4f, color_to_id

from time import monotonic

logger = logging.getLogger("OpenGL.Widget")


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget, keymap: None | Keymap = None):
        super().__init__(parent)

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._rotation_speed = 1.0
        self._scale_speed = 1.0

        # Initialize components
        self.action_handler = ActionHandler(keymap)
        self.projection_manager = ProjectionManager(width=self.size().width(), height=self.size().height())
        self.resource_manager = ResourceManager()
        self.resource_manager.add_camera(Camera("main"))
        self.resource_manager.add_scene(Scene("main"))

        self.renderer = Renderer(self.projection_manager, self.resource_manager)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._init_actions()

    def post_init(self):
        self.init_shaders()
        self.init_font_atlas()

    def init_shaders(self):
        self.resource_manager.add_shader(
            ShaderProgram(
                "default",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED), 
                FragmentShader(shaders.fragment.BLINN_PHONG)
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "text", 
                VertexShader(shaders.vertex.BILLBOARD_TEXT), 
                FragmentShader(shaders.fragment.TEXTURE)
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "transparent",
                VertexShader(shaders.vertex.COMPUTE_POSITION_INSTANCED),
                FragmentShader(shaders.fragment.FLAT_COLOR)
            )
        )
        self.resource_manager.add_shader(
            ShaderProgram(
                "picking",
                VertexShader(shaders.vertex.COMPUTE_POSITION),
                FragmentShader(shaders.fragment.FLAT_COLOR)
            )
        )

    def init_font_atlas(self):
        self.add_font_atlas("Arial.ttf", "arial", "font_atlas_arial")

    def add_font_atlas(self, font_name: str, font_atlas_name: str, font_atlas_texture_name: str):
        atlas_size = 512
        data, atlas_info = create_font_atlas(font_name, atlas_size=atlas_size)
        font_atlas = FontAtlas(font_atlas_name, atlas_info)
        texture = Texture2D(name=font_atlas_texture_name, width=atlas_size, height=atlas_size, data=data)
        self.resource_manager.add_font_atlas(font_atlas)
        self.resource_manager.add_texture(texture)

        self._build_font_atlas_geometry(font_atlas)

    def _build_font_atlas_geometry(self, font_atlas: FontAtlas):
        for char, info in font_atlas.info.items():
            u_min, v_min = info["uv_min"]
            u_max, v_max = info["uv_max"]
            width = info["width"] / info["height"]

            vertices = rect.get_vertices(left=-width, right=width, bottom=-1.0, top=1.0)
            tex_coords = rect.get_texture_coords(u_min=u_min, u_max=u_max, v_min=v_min, v_max=v_max)
            mesh = Mesh(f"{font_atlas.name}_{char}", vertices, rect.get_normals(), tex_coords)
            vao = VertexArrayObject(f"{font_atlas.name}_{char}", vertices, rect.get_normals(), tex_coords)
            self.resource_manager.add_mesh(mesh)
            self.resource_manager.add_vertex_array_object(vao)

    def clear(self):
        self.resource_manager.current_scene.clear()

    def _init_actions(self):
        self.action_handler.add_action("rotate_up", True, self.rotate_scene, -1, 0)
        self.action_handler.add_action("rotate_down", True, self.rotate_scene, 1, 0)
        self.action_handler.add_action("rotate_left", True, self.rotate_scene, 0, -1)
        self.action_handler.add_action("rotate_right", True, self.rotate_scene, 0, 1)
        self.action_handler.add_action("zoom_in", True, self.scale_scene, 1.015)
        self.action_handler.add_action("zoom_out", True, self.scale_scene, 0.975)

    def _setup_projection(self, w: int, h: int):
        glViewport(0, 0, w, h)

    @property
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    def initializeGL(self):
        self.makeCurrent()
        self.projection_manager.build_projections(self.size().width(), self.size().height())
        self._setup_projection(self.size().width(), self.size().height())
        glEnable(GL_MULTISAMPLE)

        try:
            self.post_init()
        except Exception:
            print(traceback.format_exc())

    def resize(self, w: int, h: int):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.resize(w, h)
        else:
            super().resize(w, h)

    def resizeGL(self, w: int, h: int):
        self.makeCurrent()
        self.projection_manager.build_projections(w, h)
        self._setup_projection(w, h)
        self.update()

    def paintGL(self):
        start = monotonic()
        self.renderer.paint(PaintMode.Normal)
        end = monotonic()
        print(f"paintGL: {end - start} seconds")

    def setWindowIcon(self, icon: QIcon):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.setWindowIcon(icon)
        else:
            super().setWindowIcon(icon)

    def keyPressEvent(self, event: QKeyEvent):
        self.action_handler.call_action(event, self.action_handler.keymap.match_key_event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self.action_handler.stop_action(event, self.action_handler.keymap.match_key_event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = pos - self._cursor_pos
                self.rotate_scene(diff.y(), diff.x())
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

        for event in events:
            self.action_handler.call_action(event, self.action_handler.keymap.match_wheel_event)

    def set_projection_mode(self, mode: ProjectionMode | str):
        self.makeCurrent()
        self.projection_manager.set_projection_mode(mode)
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def toggle_projection_mode(self):
        self.makeCurrent()
        self.projection_manager.toggle_projection_mode()
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def set_perspective_projection_fov(self, value: float):
        self.makeCurrent()
        self.projection_manager.perspective_projection.set_fov(value)
        self.projection_manager.build_projections(self.size().width(), self.size().height())
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def set_scene_position(self, point: QVector3D):
        self.resource_manager.current_scene.transform.set_translation(point)
        self.update()

    def set_scene_translate(self, vector: QVector3D):
        self.resource_manager.current_scene.transform.translate(vector)
        self.update()

    def set_background_color(self, color: Color4f):
        self.renderer.set_background_color(color)
        self.update()

    def rotate_scene(self, pitch: float, yaw: float, roll: float = 0.0):
        self.resource_manager.current_scene.transform.rotate(pitch, yaw, roll)
        self.update()

    def scale_scene(self, factor: float):
        self.resource_manager.current_scene.transform.scale(factor)
        self.update()

    def new_cursor_position(self, x: int, y: int):
        pass

    def render_to_image(self, width: int, height: int, transparent_bg: bool = False, crop_to_content: bool = False):
        self.makeCurrent()
        return self.renderer.render_to_image(width, height, transparent_bg, crop_to_content)

    def item_under_cursor(self) -> None | SceneNode:
        self.makeCurrent()
        image = self.renderer.picking_image(self.size().width(), self.size().height())

        x = self._cursor_pos.x()
        y = self._cursor_pos.y()

        color = image.pixelColor(x, y)
        obj_id = color_to_id(color)

        return self.resource_manager.current_scene.find_node_by_id(obj_id)
