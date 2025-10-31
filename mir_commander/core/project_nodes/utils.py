from mir_commander.plugin_system.metadata import Metadata
from mir_commander.plugin_system.project_node import ProjectNodePlugin


class BaseProjectNode(ProjectNodePlugin):
    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self.get_name(),
            version=(1, 0, 0),
            description="Core project node",
            author="Mir Commander",
            email="info@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )
