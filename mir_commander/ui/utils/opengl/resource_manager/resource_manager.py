from .camera import Camera
from .font_atlas import FontAtlas
from .mesh import Mesh
from .scene import Scene
from .shader import ShaderProgram
from .texture2d import Texture2D
from .vertex_array_object import VertexArrayObject


class ResourceManager:
    def __init__(self, fallback_mode: bool = False):
        self.fallback_mode = fallback_mode

        self._cameras: dict[str, Camera] = {}
        self._scenes: dict[str, Scene] = {}
        self._shaders: dict[str, ShaderProgram] = {}
        self._meshes: dict[str, Mesh] = {}
        self._vertex_array_objects: dict[str, VertexArrayObject] = {}
        self._textures: dict[str, Texture2D] = {}
        self._font_atlases: dict[str, FontAtlas] = {}

        self._current_camera: None | Camera = None
        self._current_scene: None | Scene = None

    @property
    def current_camera(self) -> Camera:
        return self._current_camera

    @property
    def current_scene(self) -> Scene:
        return self._current_scene

    def add_camera(self, camera: Camera):
        self._cameras[camera.name] = camera
        if not self._current_camera:
            self._current_camera = camera

    def get_camera(self, name: str) -> Camera:
        try:
            return self._cameras[name]
        except KeyError:
            raise ValueError(f"Camera `{name}` not found")

    def add_scene(self, scene: Scene):
        self._scenes[scene.name] = scene
        if not self._current_scene:
            self._current_scene = scene

    def get_scene(self, name: str) -> Scene:
        try:
            return self._scenes[name]
        except KeyError:
            raise ValueError(f"Scene `{name}` not found")

    def add_shader(self, shader: ShaderProgram):
        self._shaders[shader.name] = shader

    def get_shader(self, name: str) -> ShaderProgram:
        try:
            return self._shaders[name]
        except KeyError:
            raise ValueError(f"Shader `{name}` not found")

    def add_mesh(self, mesh: Mesh):
        self._meshes[mesh.name] = mesh

    def get_mesh(self, name: str) -> Mesh:
        try:
            return self._meshes[name]
        except KeyError:
            raise ValueError(f"Mesh `{name}` not found")

    def add_vertex_array_object(self, vertex_array_object: VertexArrayObject):
        self._vertex_array_objects[vertex_array_object.name] = vertex_array_object

    def get_vertex_array_object(self, name: str) -> VertexArrayObject:
        try:
            return self._vertex_array_objects[name]
        except KeyError:
            raise ValueError(f"Vertex array object `{name}` not found")

    def add_texture(self, texture: Texture2D):
        self._textures[texture.name] = texture

    def get_texture(self, name: str) -> Texture2D:
        try:
            return self._textures[name]
        except KeyError:
            raise ValueError(f"Texture `{name}` not found")

    def add_font_atlas(self, font_atlas: FontAtlas):
        self._font_atlases[font_atlas.name] = font_atlas

    def get_font_atlas(self, name: str) -> FontAtlas:
        try:
            return self._font_atlases[name]
        except KeyError:
            raise ValueError(f"Font atlas `{name}` not found")

    def __repr__(self):
        cameras = ",\n\t".join((str(camera) for camera in self._cameras.values()))
        scenes = ",\n\t".join((str(scene) for scene in self._scenes.values()))
        meshes = ",\n\t".join((str(mesh) for mesh in self._meshes.values()))
        vertex_array_objects = ",\n\t".join((str(vao) for vao in self._vertex_array_objects.values()))
        shaders = ",\n\t".join((str(shader) for shader in self._shaders.values()))
        textures = ",\n\t".join((str(texture) for texture in self._textures.values()))
        font_atlases = ",\n\t".join((str(font_atlas) for font_atlas in self._font_atlases.values()))

        return f"""{self.__class__.__name__}(
    cameras=[
        {cameras}
    ],
    scenes=[
        {scenes}
    ],
    shaders=[
        {shaders}
    ],
    meshes=[
        {meshes}
    ],
    vertex_array_objects=[
        {vertex_array_objects}
    ],
    textures=[
        {textures}
    ],
    font_atlases=[
        {font_atlases}
    ]
)"""
