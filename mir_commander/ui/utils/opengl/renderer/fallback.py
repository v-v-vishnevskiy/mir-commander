import logging

from PySide6.QtGui import QMatrix4x4

from OpenGL.GL import glLoadMatrixf, glUseProgram, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, glVertexPointer, glNormalPointer, glColor4f, glDrawArrays, glEnableClientState, glDisableClientState, GL_FLOAT, GL_TRIANGLES

from ..enums import PaintMode
from ..resource_manager import RenderingContainer, SceneNode
from ..utils import Color4f

from .base import BaseRenderer

logger = logging.getLogger("Renderer.Fallback")


class FallbackRenderer(BaseRenderer):
    def paint_opaque(self, rc: RenderingContainer):
        self._paint_normal(rc)

    def paint_transparent(self, rc: RenderingContainer):
        self._paint_normal(rc)

    def paint_picking(self, rc: RenderingContainer):
        self._paint_picking(rc)

    def _paint_normal(self, rc: RenderingContainer):
        transform_matrix = self._get_transform_matrix()

        last_shader_name = None

        for group_id, nodes in rc.batches:
            shader_name, model_name, texture_name, color = group_id

            # Switch shader if needed
            if shader_name != last_shader_name:
                try:
                    shader = self._resource_manager.get_shader(shader_name)
                except ValueError:
                    logger.warning(f"Shader `{shader_name}` not found, skipping group")
                    continue

                glUseProgram(shader.program)
                last_shader_name = shader_name

            self._paint_nodes(model_name, nodes, color, transform_matrix, PaintMode.Normal)

    def _paint_picking(self, rc: RenderingContainer):
        shader = self._resource_manager.get_shader("picking")
        glUseProgram(shader.program)

        transform_matrix = self._get_transform_matrix()

        for group_id, nodes in rc.batches:
            shader_name, model_name, texture_name, color = group_id

            self._paint_nodes(model_name, nodes, color, transform_matrix, PaintMode.Picking)

    def _get_transform_matrix(self) -> QMatrix4x4:
        view_matrix = self._resource_manager.current_camera.matrix
        scene_matrix = self._resource_manager.current_scene.transform.matrix
        return view_matrix * scene_matrix

    def _paint_nodes(
        self,
        model_name: str,
        nodes: list[SceneNode],
        color: Color4f,
        transform_matrix: QMatrix4x4,
        paint_mode: PaintMode,
    ):
        mesh = self._resource_manager.get_mesh(model_name)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, mesh.vertices)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, mesh.normals)

        count = int(len(mesh.vertices) / 3)

        glColor4f(*color)

        for node in nodes:
            glLoadMatrixf((transform_matrix * node.transform).data())

            if paint_mode == PaintMode.Picking:
                glColor4f(*node.picking_color)

            glDrawArrays(GL_TRIANGLES, 0, count)

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
