from collections import defaultdict

from PySide6.QtGui import QMatrix4x4

from OpenGL.GL import glLoadMatrixf, glUseProgram, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, glVertexPointer, glNormalPointer, glColor4f, glDrawArrays, glEnableClientState, glDisableClientState, GL_FLOAT, GL_TRIANGLES

from ..enums import PaintMode
from ..resource_manager import SceneNode

from .base import BaseRenderer


class FallbackRenderer(BaseRenderer):
    def paint_opaque(self, nodes: list[SceneNode]):
        self._paint_normal(nodes)

    def paint_transparent(self, nodes: list[SceneNode]):
        self._paint_normal(nodes)

    def paint_picking(self, nodes: list[SceneNode]):
        self._paint_picking(nodes)

    def _paint_normal(self, nodes: list[SceneNode]):
        transform_matrix = self._get_transform_matrix()

        nodes_by_group = defaultdict(list)
        for node in nodes:
            nodes_by_group[(node.mesh, node.shader)].append(node)

        for group, nodes in nodes_by_group.items():
            mesh_name, shader_name = group
            mesh = self._resource_manager.get_mesh(mesh_name)
            shader = self._resource_manager.get_shader(shader_name)
            glUseProgram(shader.program)
            self._paint_nodes(nodes, transform_matrix, mesh.vertices, mesh.normals, PaintMode.Normal)

    def _paint_picking(self, nodes: list[SceneNode]):
        shader = self._resource_manager.get_shader("picking")
        glUseProgram(shader.program)

        transform_matrix = self._get_transform_matrix()

        nodes_by_mesh_name = defaultdict(list)
        for node in nodes:
            nodes_by_mesh_name[node.mesh].append(node)

        for mesh_name, nodes in nodes_by_mesh_name.items():
            mesh = self._resource_manager.get_mesh(mesh_name)
            self._paint_nodes(nodes, transform_matrix, mesh.vertices, mesh.normals, PaintMode.Picking)

    def _get_transform_matrix(self) -> QMatrix4x4:
        view_matrix = self._resource_manager.current_camera.matrix
        scene_matrix = self._resource_manager.current_scene.transform.matrix
        return view_matrix * scene_matrix

    def _paint_nodes(self, nodes: list[SceneNode], transform_matrix: QMatrix4x4, vertices: list[float], normals: list[float], paint_mode: PaintMode):
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, vertices)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, normals)

        count = int(len(vertices) / 3)

        for node in nodes:
            glLoadMatrixf((transform_matrix * node.transform).data())

            if paint_mode == PaintMode.Picking:
                glColor4f(*node.picking_color)
            else:
                glColor4f(*node.color)

            glDrawArrays(GL_TRIANGLES, 0, count)

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
