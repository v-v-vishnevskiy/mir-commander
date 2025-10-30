from mir_commander.plugin_system.project_node import ProjectNodeDataPlugin, ProjectNodePlugin


class UnexData(ProjectNodeDataPlugin): ...


class UnexNode(ProjectNodePlugin):
    def get_type(self) -> str:
        return "unex"

    def get_name(self) -> str:
        return "UNEX"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/unex.png"

    def get_model_class(self) -> type[UnexData]:
        return UnexData

    def get_default_program_name(self) -> None | str:
        return None

    def get_program_names(self) -> list[str]:
        return []
