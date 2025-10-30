from .utils import BaseProjectNode


class UnexNode(BaseProjectNode):
    def get_type(self) -> str:
        return "unex"

    def get_name(self) -> str:
        return "UNEX"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/unex.png"

    def get_model_class(self) -> None:
        return None

    def get_default_program_name(self) -> None | str:
        return None

    def get_program_names(self) -> list[str]:
        return []
