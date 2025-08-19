from mir_commander.ui.utils.opengl.scene import OpaqueNode


class BaseGraphicsNode(OpaqueNode):
    def set_under_cursor(self, value: bool):
        pass

    def get_text(self) -> str:
        return ""

    def toggle_selection(self) -> bool:
        return False
