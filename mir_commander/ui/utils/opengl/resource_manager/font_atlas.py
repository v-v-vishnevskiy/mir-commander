from ..font_atlas import FontAtlasInfo
from .base import Resource


class FontAtlas(Resource):
    def __init__(self, name: str, info: FontAtlasInfo):
        super().__init__(name)
        self.info = info
