from .base import Resource


class FontAtlas(Resource):
    def __init__(self, name: str, info: dict):
        super().__init__(name)
        self.info = info
