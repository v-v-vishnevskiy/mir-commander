from collections import defaultdict

from OpenGL.GL import glLoadMatrixf, glUseProgram, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, glVertexPointer, glNormalPointer, glColor4f, glDrawArrays, glEnableClientState, glDisableClientState, GL_FLOAT, GL_TRIANGLES

from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.shaders import fragment_fallback, vertex_fallback

from ..graphics_items.item import Item
from ..enums import PaintMode

from .base import BaseRenderer


class FallbackRenderer(BaseRenderer):
    def init_shaders(self):
        self._shaders["default"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.BLINN_PHONG)
        )
        self._shaders["transparent"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.FLAT_COLOR)
        )
        self._shaders["picking"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.FLAT_COLOR)
        )

    def paint_opaque(self, items: list[Item]):
        self._paint(self._shaders["default"], items, PaintMode.Normal)

    def paint_transparent(self, items: list[Item]):
        self._paint(self._shaders["transparent"], items, PaintMode.Normal)

    def paint_picking(self, items: list[Item]):
        self._paint(self._shaders["picking"], items, PaintMode.Picking)

    def _paint(self, shader: ShaderProgram, items: list[Item], paint_mode: PaintMode):
        glUseProgram(shader.program)

        items_by_mesh_id = defaultdict(list)
        for item in items:
            items_by_mesh_id[item.mesh_id].append(item)

        for items in items_by_mesh_id.values():
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, items[0]._mesh_data.vertices)

            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, items[0]._mesh_object.normals)

            count = int(len(items[0]._mesh_data.vertices) / 3)

            for item in items:
                glLoadMatrixf((self._camera.view_matrix * self._scene.get_transform * item.get_transform).data())

                if paint_mode == PaintMode.Picking:
                    glColor4f(*item.picking_color)
                else:
                    glColor4f(*item.color)

                glDrawArrays(GL_TRIANGLES, 0, count)

            glDisableClientState(GL_NORMAL_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)
