from mir_commander.api.metadata import Metadata
from mir_commander.api.project_node import ProjectNodePlugin as BaseProjectNodePlugin


class ProjectNodePlugin(BaseProjectNodePlugin):
    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self.get_name(),
            version=(1, 0, 0),
            description="Core project node",
            author="Mir Commander",
            email="support@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )
